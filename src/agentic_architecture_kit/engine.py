from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import subprocess
from collections import Counter, deque
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .model import Finding, ValidationContext
from .norms import markdown_sections, read_reference_document, reference_section, split_reference


def _finding(
    rule: str,
    status: str,
    scope: str,
    message: str,
    **evidence: object,
) -> Finding:
    return Finding(rule, status, scope, message, evidence)


def _repo_path(context: ValidationContext, value: str) -> Path:
    candidate = (context.root / value).resolve()
    try:
        candidate.relative_to(context.root.resolve())
    except ValueError as error:
        raise ValueError(f"Policy path escapes repository root: {value}") from error
    return candidate


def _display_path(context: ValidationContext, path: Path) -> str:
    try:
        return path.resolve().relative_to(context.root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _declared_projects(context: ValidationContext) -> dict[str, dict]:
    return {item["path"]: item for item in context.policy["projects"]}


def _namespace_owners(context: ValidationContext, namespace: str) -> list[tuple[str, str, bool]]:
    owners: list[tuple[str, str, bool]] = []
    for module in context.policy["modules"]:
        if any(fnmatch.fnmatchcase(namespace, pattern) for pattern in module.get("namespacePatterns", [])):
            is_contract = any(
                fnmatch.fnmatchcase(namespace, pattern)
                for pattern in module.get("contractNamespacePatterns", [])
            )
            owners.append(("module", module["id"], is_contract))
    for host in context.policy["hosts"]:
        if any(fnmatch.fnmatchcase(namespace, pattern) for pattern in host.get("namespacePatterns", [])):
            owners.append(("host", host["id"], False))
    return owners


def _namespace_owner(context: ValidationContext, namespace: str) -> tuple[str, str, bool] | None:
    owners = _namespace_owners(context, namespace)
    return owners[0] if len(owners) == 1 else None


def _source_project_paths(source_path: str, projects: dict[str, dict[str, Any]]) -> list[str]:
    candidates: list[tuple[int, str]] = []
    for project_path in projects:
        project_root = Path(project_path).parent.as_posix()
        if project_root == "." or source_path.startswith(project_root.rstrip("/") + "/"):
            candidates.append((len(project_root), project_path))
    if not candidates:
        return []
    most_specific = max(length for length, _ in candidates)
    return sorted(path for length, path in candidates if length == most_specific)


def _source_expected_owners(context: ValidationContext, source_path: str) -> tuple[list[tuple[str, str]], list[str]]:
    candidates: list[tuple[int, str, str, str]] = []
    for kind, declarations in (("module", context.policy["modules"]), ("host", context.policy["hosts"])):
        for declaration in declarations:
            root = declaration["root"].rstrip("/") or "."
            if root == "." or source_path == root or source_path.startswith(root + "/"):
                candidates.append((len(root), kind, declaration["id"], root))
    if candidates:
        most_specific = max(length for length, _, _, _ in candidates)
        owners = sorted({(kind, owner_id) for length, kind, owner_id, _ in candidates if length == most_specific})
        evidence = sorted({root for length, _, _, root in candidates if length == most_specific})
        return owners, evidence

    projects = _declared_projects(context)
    project_paths = _source_project_paths(source_path, projects)
    owners = sorted({
        (projects[path]["owner"]["kind"], projects[path]["owner"]["id"])
        for path in project_paths
    })
    return owners, project_paths


def _observed_namespace_expected_owners(
    context: ValidationContext,
    namespace: str,
) -> tuple[list[tuple[str, str]], list[str]]:
    owners: set[tuple[str, str]] = set()
    evidence: set[str] = set()
    projects = _declared_projects(context)
    for item in context.observed.source_namespaces:
        if not (
            namespace == item.namespace
            or namespace.startswith(item.namespace + ".")
            or item.namespace.startswith(namespace + ".")
        ):
            continue
        if (
            _source_belongs_only_to_test_projects(item.source_path, projects)
            and item.namespace != namespace
            and item.namespace.startswith(namespace + ".")
        ):
            continue
        expected, sources = _source_expected_owners(context, item.source_path)
        owners.update(expected)
        evidence.update(sources or [item.source_path])
    for project in context.observed.projects:
        root_namespace = project.root_namespace
        if not root_namespace or not (
            namespace == root_namespace
            or namespace.startswith(root_namespace + ".")
            or root_namespace.startswith(namespace + ".")
        ):
            continue
        declaration = projects.get(project.path)
        if declaration:
            if (
                declaration["role"] == "test"
                and root_namespace != namespace
                and root_namespace.startswith(namespace + ".")
            ):
                continue
            owners.add((declaration["owner"]["kind"], declaration["owner"]["id"]))
            evidence.add(project.path)
    return sorted(owners), sorted(evidence)


def _project_matches(declaration: dict, selector: dict) -> bool:
    owner = declaration["owner"]
    return (
        ("ownerKind" not in selector or selector["ownerKind"] == owner["kind"])
        and ("ownerId" not in selector or selector["ownerId"] == owner["id"])
        and ("role" not in selector or selector["role"] == declaration["role"])
        and ("pathPattern" not in selector or fnmatch.fnmatchcase(declaration["path"], selector["pathPattern"]))
    )


def _references_resolve(context: ValidationContext, references: list[str]) -> list[str]:
    missing: list[str] = []
    for reference in references:
        try:
            _, section = reference_section(context.root, reference)
            _, anchor = split_reference(reference)
            if anchor is not None and section is None:
                missing.append(reference)
        except (FileNotFoundError, ValueError):
            missing.append(reference)
    return missing


def _rule_policy_valid(context: ValidationContext) -> list[Finding]:
    missing: list[dict[str, str]] = []
    groups = (
        context.policy.get("modules", []),
        context.policy.get("hosts", []),
        context.policy.get("projects", []),
        context.policy.get("allowedProjectDependencies", []),
        context.policy.get("dependencyRules", []),
    )
    for items in groups:
        for item in items:
            for reference in item.get("decisionRefs", []):
                if not _repo_path(context, reference).is_file():
                    missing.append({"reference": reference, "subject": item.get("id", item.get("path", item.get("from", "dependency-rule")))})
    if missing:
        return [_finding("POL001", "FAIL", _display_path(context, context.policy_path), "Project policy references missing architecture decisions.", missing=missing)]
    return [_finding("POL001", "PASS", _display_path(context, context.policy_path), "Project policy is valid and its declared decisions resolve.")]


def _rule_architecture_matches(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    declared_modules = {item["root"] for item in context.policy["modules"]}
    observed_modules = set(context.observed.modules)
    declared_hosts = {item["root"] for item in context.policy["hosts"]}
    observed_hosts = set(context.observed.hosts)
    declared_projects = _declared_projects(context)
    observed_projects = context.observed.projects_by_path

    comparisons = (
        ("modules", declared_modules, observed_modules, context.policy["roots"]["modules"]),
        ("hosts", declared_hosts, observed_hosts, context.policy["roots"]["hosts"]),
        ("projects", set(declared_projects), set(observed_projects), "."),
    )
    for kind, declared, observed, scope in comparisons:
        for missing in sorted(declared - observed):
            results.append(
                _finding(
                    "ARC001",
                    "FAIL",
                    missing,
                    f"Declared {kind[:-1]} is absent from the observed architecture.",
                    declared=missing,
                )
            )
        for undeclared in sorted(observed - declared):
            results.append(
                _finding(
                    "ARC001",
                    "FAIL",
                    undeclared,
                    f"Observed {kind[:-1]} is not declared by project policy.",
                    observed=undeclared,
                )
            )

    for path in sorted(set(declared_projects) & set(observed_projects)):
        expected_name = declared_projects[path].get("name")
        actual_name = observed_projects[path].name
        if expected_name and expected_name != actual_name:
            results.append(
                _finding(
                    "ARC001",
                    "FAIL",
                    path,
                    "Declared project name does not match the observed assembly name.",
                    declared=expected_name,
                    observed=actual_name,
                )
            )
        declared_test = declared_projects[path]["role"] == "test"
        observed_test = observed_projects[path].role_hint == "test"
        if declared_test != observed_test:
            results.append(
                _finding(
                    "ARC001",
                    "FAIL",
                    path,
                    "Declared test role does not match observed test-project evidence.",
                    declaredRole=declared_projects[path]["role"],
                    observedRoleHint=observed_projects[path].role_hint,
                )
            )

    for item in context.observed.source_namespaces:
        if _source_belongs_only_to_test_projects(item.source_path, declared_projects):
            continue
        expected_owners, expected_from = _source_expected_owners(context, item.source_path)
        issue = _namespace_resolution_issue(
            context,
            item.namespace,
            expected_owners,
            expected_from or [item.source_path],
        )
        if issue:
            results.append(
                _finding(
                    "ARC001",
                    "FAIL" if expected_owners else "REVIEW_REQUIRED",
                    item.source_path,
                    "Observed source namespace does not resolve to exactly its declared owner.",
                    **issue,
                )
            )

    for project in context.observed.projects:
        for reference in project.references:
            if reference not in observed_projects:
                results.append(
                    _finding(
                        "ARC001",
                        "FAIL",
                        project.path,
                        "Project reference does not resolve to an observed project.",
                        target=reference,
                    )
                )

    if not results:
        results.append(
            _finding(
                "ARC001",
                "PASS",
                ".",
                "Declared modules, hosts, projects, names, test roles, and source namespaces match the observed repository.",
                modules=sorted(observed_modules),
                hosts=sorted(observed_hosts),
                projects=sorted(observed_projects),
            )
        )
    return results


def _rule_module_contract(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    file_name = context.policy["moduleContract"]["fileName"]
    for module_root in context.observed.modules:
        contract_path = _repo_path(context, f"{module_root}/{file_name}")
        router_path = _repo_path(context, f"{module_root}/AGENTS.md")
        missing = [
            path.relative_to(context.root).as_posix()
            for path in (contract_path, router_path)
            if not path.is_file()
        ]
        contract_key = contract_path.relative_to(context.root).as_posix()
        contract_errors = context.contract_errors.get(contract_key, [])
        if missing or contract_errors:
            results.append(
                _finding(
                    "MOD001",
                    "FAIL",
                    module_root,
                    "Module is missing its semantic contract or local agent router.",
                    missing=missing,
                    contractErrors=contract_errors,
                )
            )
        else:
            results.append(
                _finding(
                    "MOD001",
                    "PASS",
                    module_root,
                    "Module has a semantic contract and local agent router.",
                    contract=contract_path.relative_to(context.root).as_posix(),
                    router=router_path.relative_to(context.root).as_posix(),
                )
            )
    if not context.observed.modules:
        status = "FAIL" if context.observed.projects or context.observed.source_files else "NOT_APPLICABLE"
        message = "No module was observed for existing product artifacts." if status == "FAIL" else "The repository has no product artifacts requiring a module yet."
        results.append(_finding("MOD001", status, context.policy["roots"]["modules"], message))
    return results


def _rule_module_identity(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    file_name = context.policy["moduleContract"]["fileName"]
    for module_root in context.observed.modules:
        contract_key = f"{module_root}/{file_name}"
        contract = context.contracts.get(contract_key)
        if contract is None:
            results.append(
                _finding("MOD002", "FAIL", contract_key, "Module contract could not be loaded.")
            )
            continue
        expected = Path(module_root).name.lower()
        actual = str(contract.get("id", ""))
        if actual != expected:
            results.append(
                _finding(
                    "MOD002",
                    "FAIL",
                    contract_key,
                    "Module contract id does not match its directory.",
                    expected=expected,
                    observed=actual,
                )
            )
        else:
            results.append(
                _finding("MOD002", "PASS", contract_key, "Module contract id matches its directory.", id=actual)
            )
    return results or [
        _finding(
            "MOD002",
            "NOT_APPLICABLE",
            context.policy["roots"]["modules"],
            "The repository has no module identity to validate yet.",
        )
    ]


def _rule_functional_modules(context: ValidationContext) -> list[Finding]:
    technical = {name.casefold() for name in context.policy["technicalModuleNames"]}
    bad = [root for root in context.observed.modules if Path(root).name.casefold() in technical]
    if bad:
        return [
            _finding(
                "MOD003",
                "FAIL",
                root,
                "Technical category is declared as a product module.",
                module=Path(root).name,
            )
            for root in bad
        ]
    return [
        _finding(
            "MOD003",
            "PASS",
            context.policy["roots"]["modules"],
            "No technical category is used as a product module.",
        )
    ]


def _rule_feature_ownership(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    for module in context.policy["modules"]:
        feature_root = module.get("featureRoot")
        declared = set(module.get("featureAreas", []))
        if feature_root is None:
            results.append(
                _finding(
                    "FEAT001",
                    "NOT_APPLICABLE",
                    module["root"],
                    "Module declares no feature root.",
                )
            )
            continue
        root_path = _repo_path(context, feature_root)
        observed = {path.name for path in root_path.iterdir() if path.is_dir()} if root_path.is_dir() else set()
        mismatches = False
        for missing in sorted(declared - observed):
            mismatches = True
            results.append(
                _finding("FEAT001", "FAIL", f"{feature_root}/{missing}", "Declared feature area is absent.")
            )
        for undeclared in sorted(observed - declared):
            mismatches = True
            results.append(
                _finding(
                    "FEAT001",
                    "FAIL",
                    f"{feature_root}/{undeclared}",
                    "Observed root feature area is not declared by project policy.",
                )
            )
        if not mismatches:
            results.append(
                _finding(
                    "FEAT001",
                    "REVIEW_REQUIRED",
                    feature_root,
                    "Feature roots match policy; semantic cohesion still requires review.",
                    featureAreas=sorted(observed),
                )
            )
    return results


def _rule_hosts_are_adapters(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    for host in context.policy["hosts"]:
        host_root = _repo_path(context, host["root"])
        patterns = host.get("allowedSourcePatterns", [])
        if host_root.is_file():
            sources = [host_root.name] if host["root"] in context.observed.source_files else []
        else:
            host_prefix = host["root"].rstrip("/") + "/"
            sources = [
                source[len(host_prefix):]
                for source in context.observed.source_files
                if source.startswith(host_prefix)
            ]
        if not patterns and sources:
            results.append(
                _finding(
                    "HOST001",
                    "REVIEW_REQUIRED",
                    host["root"],
                    "Host source exists but policy does not classify its allowed adapter paths.",
                    sourceFiles=sorted(sources),
                )
            )
            continue
        disallowed = [source for source in sources if not any(fnmatch.fnmatchcase(source, pattern) for pattern in patterns)]
        if disallowed:
            results.append(
                _finding(
                    "HOST001",
                    "FAIL",
                    host["root"],
                    "Host contains source outside its declared adapter and composition paths.",
                    sourceFiles=sorted(disallowed),
                    allowedPatterns=patterns,
                )
            )
        else:
            results.append(
                _finding(
                    "HOST001",
                    "PASS",
                    host["root"],
                    "Host source is confined to declared adapter and composition paths.",
                    sourceFiles=sorted(sources),
                )
            )
    return results


def _dependency_path(graph: dict[str, tuple[str, ...]], start: str, targets: set[str]) -> list[str] | None:
    queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        for target in graph.get(node, ()):
            if target in targets:
                return path + [target]
            if target not in visited:
                visited.add(target)
                queue.append((target, path + [target]))
    return None


def _source_belongs_only_to_test_projects(source_path: str, projects: dict[str, dict[str, Any]]) -> bool:
    project_paths = _source_project_paths(source_path, projects)
    if not project_paths:
        return False
    return all(projects[path]["role"] == "test" for path in project_paths)


def _namespace_resolution_issue(
    context: ValidationContext,
    namespace: str,
    expected_owners: list[tuple[str, str]],
    expected_from: list[str],
) -> dict[str, object] | None:
    owners = _namespace_owners(context, namespace)
    matched_owners = sorted({(kind, owner_id) for kind, owner_id, _ in owners})
    if len(owners) == 1 and (not expected_owners or matched_owners == expected_owners):
        return None
    return {
        "namespace": namespace,
        "expectedFrom": expected_from,
        "expectedOwners": [f"{kind}:{owner_id}" for kind, owner_id in expected_owners],
        "matchedOwners": [f"{kind}:{owner_id}" for kind, owner_id in matched_owners],
        "reason": "ambiguous" if len(owners) > 1 else "unresolved" if not owners else "owner-mismatch",
    }


def _rule_modules_do_not_depend_on_hosts(context: ValidationContext) -> list[Finding]:
    projects = _declared_projects(context)
    graph = {project.path: project.references for project in context.observed.projects}
    module_projects = {
        path
        for path, item in projects.items()
        if item["owner"]["kind"] == "module" and item["role"] != "test"
    }
    host_projects = {
        path for path, item in projects.items() if item["owner"]["kind"] == "host"
    }
    findings: list[Finding] = []
    resolution_groups: dict[tuple[str, str], dict[str, Any]] = {}
    for project in sorted(module_projects):
        path = _dependency_path(graph, project, host_projects)
        if path:
            findings.append(
                _finding(
                    "DEP001",
                    "FAIL",
                    project,
                    "Production module project depends on a host project.",
                    dependencyPath=path,
                )
            )
    for dependency in context.observed.source_dependencies:
        if _source_belongs_only_to_test_projects(dependency.source_path, projects):
            continue
        source_owners, source_evidence = _source_expected_owners(context, dependency.source_path)
        target_owners, target_evidence = _observed_namespace_expected_owners(
            context,
            dependency.target_namespace,
        )
        source_namespace_observed = any(
            item.source_path == dependency.source_path
            and item.namespace == dependency.source_namespace
            for item in context.observed.source_namespaces
        )
        resolution_issues = [
            issue
            for issue in (
                _namespace_resolution_issue(
                    context,
                    dependency.source_namespace,
                    source_owners,
                    source_evidence or [dependency.source_path],
                )
                if source_namespace_observed else None,
                _namespace_resolution_issue(
                    context,
                    dependency.target_namespace,
                    target_owners,
                    target_evidence,
                )
                if target_owners else None,
            )
            if issue is not None
        ]
        if resolution_issues:
            for issue in resolution_issues:
                issue_key = json.dumps(issue, sort_keys=True, separators=(",", ":"))
                group = resolution_groups.setdefault(
                    (dependency.source_path, issue_key),
                    {
                        "scope": dependency.source_path,
                        "issue": issue,
                        "affectedEdges": [],
                    },
                )
                group["affectedEdges"].append({
                    "sourceNamespace": dependency.source_namespace,
                    "targetNamespace": dependency.target_namespace,
                    "observation": dependency.kind,
                    "confidence": dependency.confidence,
                })
            continue
        source = _namespace_owner(context, dependency.source_namespace)
        target = _namespace_owner(context, dependency.target_namespace)
        if source and target and source[0] == "module" and target[0] == "host":
            findings.append(
                _finding(
                    "DEP001",
                    "FAIL",
                    dependency.source_path,
                    "Module source imports a host-owned namespace.",
                    sourceNamespace=dependency.source_namespace,
                    targetNamespace=dependency.target_namespace,
                    observation=dependency.kind,
                    confidence=dependency.confidence,
                )
            )
    for key in sorted(resolution_groups):
        group = resolution_groups[key]
        unique_edges = {
            json.dumps(edge, sort_keys=True, separators=(",", ":")): edge
            for edge in group["affectedEdges"]
        }
        findings.append(
            _finding(
                "DEP001",
                "REVIEW_REQUIRED",
                group["scope"],
                "A repository-local namespace cannot be assigned to exactly one declared owner; DEP001 cannot prove the affected edge directions.",
                namespaceResolutionIssue=group["issue"],
                affectedEdges=[unique_edges[value] for value in sorted(unique_edges)],
            )
        )
    return findings or [
        _finding(
            "DEP001",
            "PASS",
            ".",
            "No production module-owned project or source namespace depends on a host.",
            evaluatedProjectEdges=sum(
                len(item.references)
                for item in context.observed.projects
                if projects.get(item.path, {}).get("role") != "test"
            ),
            excludedTestProjectEdges=sum(
                len(item.references)
                for item in context.observed.projects
                if projects.get(item.path, {}).get("role") == "test"
            ),
            evaluatedSourceEdges=sum(
                not _source_belongs_only_to_test_projects(item.source_path, projects)
                for item in context.observed.source_dependencies
            ),
            excludedTestSourceEdges=sum(
                _source_belongs_only_to_test_projects(item.source_path, projects)
                for item in context.observed.source_dependencies
            ),
        )
    ]


def _rule_cross_module_contracts(context: ValidationContext) -> list[Finding]:
    declarations = _declared_projects(context)
    violations: list[Finding] = []
    cross_edges = 0
    for project in context.observed.projects:
        source = declarations.get(project.path)
        if source is None or source["owner"]["kind"] != "module":
            continue
        for reference in project.references:
            target = declarations.get(reference)
            if target is None or target["owner"]["kind"] != "module":
                continue
            if source["owner"]["id"] == target["owner"]["id"]:
                continue
            cross_edges += 1
            if target["role"] != "contracts" and not target.get("publicContract", False):
                violations.append(
                    _finding(
                        "DEP002",
                        "FAIL",
                        project.path,
                        "Cross-module dependency does not target a declared public contract.",
                        target=reference,
                    )
                )
    for dependency in context.observed.source_dependencies:
        source = _namespace_owner(context, dependency.source_namespace)
        target = _namespace_owner(context, dependency.target_namespace)
        if not source or not target or source[0] != "module" or target[0] != "module" or source[1] == target[1]:
            continue
        cross_edges += 1
        if not target[2]:
            violations.append(
                _finding(
                    "DEP002",
                    "FAIL",
                    dependency.source_path,
                    "Cross-module source import does not target a declared contract namespace.",
                    sourceNamespace=dependency.source_namespace,
                    targetNamespace=dependency.target_namespace,
                    observation=dependency.kind,
                    confidence=dependency.confidence,
                )
            )
    if violations:
        return violations
    if cross_edges == 0:
        return [_finding("DEP002", "NOT_APPLICABLE", ".", "No cross-module project dependency exists.")]
    return [_finding("DEP002", "PASS", ".", "Cross-module dependencies target public contracts.")]


def _rule_allowed_dependencies(context: ValidationContext) -> list[Finding]:
    allowed = {
        (item["from"], item["to"])
        for item in context.policy["allowedProjectDependencies"]
    }
    actual = {
        (project.path, target)
        for project in context.observed.projects
        for target in project.references
        if target in context.observed.projects_by_path
    }
    declarations = _declared_projects(context)
    dependency_rules = context.policy.get("dependencyRules", [])
    allowed_owner_pairs = {
        (
            (declarations[source]["owner"]["kind"], declarations[source]["owner"]["id"]),
            (declarations[target]["owner"]["kind"], declarations[target]["owner"]["id"]),
        )
        for source, target in allowed
        if source in declarations and target in declarations
    }
    unexpected: list[tuple[str, str]] = []
    for source, target in sorted(actual - allowed):
        if source not in declarations or target not in declarations:
            unexpected.append((source, target))
            continue
        source_declaration = declarations[source]
        target_declaration = declarations[target]
        if any(
            _project_matches(source_declaration, rule["from"])
            and _project_matches(target_declaration, rule["to"])
            for rule in dependency_rules
        ):
            continue
        unexpected.append((source, target))
    findings = [
            _finding(
                "DEP003",
                "FAIL",
                source,
                "Observed project dependency is not allowed by project policy.",
                target=target,
            )
            for source, target in unexpected
        ]

    source_evidence: list[dict[str, str]] = []
    for dependency in context.observed.source_dependencies:
        source_owner = _namespace_owner(context, dependency.source_namespace)
        target_owner = _namespace_owner(context, dependency.target_namespace)
        if not source_owner or not target_owner or source_owner[:2] == target_owner[:2]:
            continue
        source_declaration = {
            "owner": {"kind": source_owner[0], "id": source_owner[1]},
            "role": "host" if source_owner[0] == "host" else "contracts" if source_owner[2] else "application",
            "path": dependency.source_path,
        }
        target_declaration = {
            "owner": {"kind": target_owner[0], "id": target_owner[1]},
            "role": "host" if target_owner[0] == "host" else "contracts" if target_owner[2] else "application",
            "path": dependency.target_namespace,
        }
        edge = ((source_owner[0], source_owner[1]), (target_owner[0], target_owner[1]))
        authorized = edge in allowed_owner_pairs or any(
            _project_matches(source_declaration, rule["from"])
            and _project_matches(target_declaration, rule["to"])
            for rule in dependency_rules
        )
        evidence = {
            "from": f"{source_owner[0]}:{source_owner[1]}",
            "to": f"{target_owner[0]}:{target_owner[1]}",
            "sourcePath": dependency.source_path,
            "targetNamespace": dependency.target_namespace,
            "confidence": dependency.confidence,
        }
        source_evidence.append(evidence)
        if not authorized:
            findings.append(
                _finding(
                    "DEP003",
                    "FAIL",
                    dependency.source_path,
                    "Observed source dependency is not allowed by project policy.",
                    **evidence,
                )
            )

    if findings:
        return findings
    return [
        _finding(
            "DEP003",
            "PASS",
            ".",
            "Every observed project and owned source dependency is allowed by project policy.",
            projectDependencies=[{"from": source, "to": target} for source, target in sorted(actual)],
            sourceDependencies=source_evidence,
        )
    ]


def _rule_data_ownership(context: ValidationContext) -> list[Finding]:
    owners: dict[str, list[str]] = {}
    file_name = context.policy["moduleContract"]["fileName"]
    for module in context.policy["modules"]:
        contract = context.contracts.get(f"{module['root']}/{file_name}", {})
        authoritative = contract.get("ownership", {}).get("authoritative_data", [])
        if isinstance(authoritative, list):
            for item in authoritative:
                owners.setdefault(str(item), []).append(module["id"])
    duplicates = {item: values for item, values in owners.items() if len(values) > 1}
    if duplicates:
        return [
            _finding(
                "OWN001",
                "FAIL",
                ".",
                "Authoritative data has more than one declared owner.",
                duplicates=duplicates,
            )
        ]
    if not owners:
        return [_finding("OWN001", "NOT_APPLICABLE", ".", "No authoritative data is declared.")]
    return [
        _finding(
            "OWN001",
            "REVIEW_REQUIRED",
            ".",
            "Declared data ownership is unique; observed write access requires a data-access analyzer.",
            owners=owners,
        )
    ]


def _rule_no_speculative_structure(context: ValidationContext) -> list[Finding]:
    forbidden = set(context.policy["forbiddenDirectoryNames"])
    ignored = {".git", ".dotnet-home", "bin", "obj", "node_modules"}
    violations: list[Finding] = []
    for search_root in context.policy["structureSearchRoots"]:
        base = _repo_path(context, search_root)
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_dir() or any(part in ignored for part in path.parts):
                continue
            if path.name in forbidden:
                violations.append(
                    _finding(
                        "STR001",
                        "FAIL",
                        path.relative_to(context.root).as_posix(),
                        "Forbidden catch-all directory was observed.",
                        directoryName=path.name,
                    )
                )

    structural = set(context.policy["moduleContract"]["forbiddenStructuralFields"])
    file_name = context.policy["moduleContract"]["fileName"]
    for module in context.policy["modules"]:
        contract_path = f"{module['root']}/{file_name}"
        contract = context.contracts.get(contract_path, {})
        fields = sorted(structural.intersection(contract))
        if fields:
            violations.append(
                _finding(
                    "STR001",
                    "FAIL",
                    contract_path,
                    "Module contract duplicates structural facts that must be observed.",
                    fields=fields,
                )
            )
    return violations or [
        _finding(
            "STR001",
            "PASS",
            ".",
            "Mechanical speculative-structure checks passed; material boundary changes are governed by CHG001 and repository approval policy.",
            directories=list(context.observed.directories),
            modules=list(context.observed.modules),
            hosts=list(context.observed.hosts),
        )
    ]


def _architecture_items(policy: dict) -> dict[str, dict[str, dict]]:
    def keyed(items: list[dict]) -> dict[str, dict]:
        return {
            hashlib.sha256(json.dumps(item, sort_keys=True, separators=(",", ":")).encode()).hexdigest(): item
            for item in items
        }

    return {
        "module": keyed(policy.get("modules", [])),
        "host": keyed(policy.get("hosts", [])),
        "project": keyed(policy.get("projects", [])),
        "dependency": keyed(policy.get("allowedProjectDependencies", [])),
        "dependencyRule": keyed(policy.get("dependencyRules", [])),
    }


def _rule_policy_growth(context: ValidationContext) -> list[Finding]:
    if context.base_policy is None:
        return [_finding("CHG001", "NOT_APPLICABLE", ".", "No base policy was supplied for architecture-growth comparison.")]
    current = _architecture_items(context.policy)
    base = _architecture_items(context.base_policy)
    findings: list[Finding] = []
    for kind, current_items in current.items():
        for key in sorted(set(current_items) - set(base[kind])):
            item = current_items[key]
            references = item.get("decisionRefs", [])
            scope_candidates = (item.get("root"), item.get("path"), item.get("from"))
            scope = next(
                (candidate for candidate in scope_candidates if isinstance(candidate, str)),
                ".agentic/policies/architecture/project-policy.json",
            )
            if not references:
                findings.append(
                    _finding(
                        "CHG001",
                        "FAIL",
                        scope,
                        f"New or materially changed architecture {kind} has no decision reference.",
                        addition=item,
                        baseRevision=context.base_revision,
                    )
                )
                continue
            missing = _references_resolve(context, references)
            if missing:
                findings.append(
                    _finding(
                        "CHG001",
                        "FAIL",
                        scope,
                        f"New or materially changed architecture {kind} references a missing decision.",
                        addition=item,
                        missing=missing,
                        baseRevision=context.base_revision,
                    )
                )
            else:
                findings.append(
                    _finding(
                        "CHG001",
                        "REVIEW_REQUIRED",
                        scope,
                        f"New or materially changed architecture {kind} is documented and requires an authority review.",
                        addition=item,
                        decisionRefs=references,
                        baseRevision=context.base_revision,
                    )
                )

    if context.base_norms is not None:
        current_documents = {
            item["reference"]: item
            for item in context.norms.get("documents", [])
            if isinstance(item, dict) and isinstance(item.get("reference"), str)
        }
        base_documents = {
            item["reference"]: item
            for item in context.base_norms.get("documents", [])
            if isinstance(item, dict) and isinstance(item.get("reference"), str)
        }
        for reference, previous in sorted(base_documents.items()):
            if previous.get("enforcer") == "human":
                continue
            current_document = current_documents.get(reference)
            if current_document is None:
                findings.append(
                    _finding(
                        "CHG001",
                        "FAIL",
                        reference,
                        "Normative material was removed without retaining an explicit enforcement classification.",
                        previousEnforcer=previous.get("enforcer"),
                        baseRevision=context.base_revision,
                    )
                )
                continue
            if current_document.get("enforcer") != "human":
                continue
            references = current_document.get("decisionRefs", [])
            if not references:
                findings.append(
                    _finding(
                        "CHG001",
                        "FAIL",
                        reference,
                        "Normative material was reclassified as human guidance without a decision reference.",
                        previousEnforcer=previous.get("enforcer"),
                        currentEnforcer="human",
                        baseRevision=context.base_revision,
                    )
                )
                continue
            missing = _references_resolve(context, references)
            if missing:
                findings.append(
                    _finding(
                        "CHG001",
                        "FAIL",
                        reference,
                        "Human reclassification references a missing decision.",
                        missing=missing,
                        baseRevision=context.base_revision,
                    )
                )
            else:
                findings.append(
                    _finding(
                        "CHG001",
                        "REVIEW_REQUIRED",
                        reference,
                        "Reducing normative enforcement to human guidance requires authority review.",
                        decisionRefs=references,
                        previousEnforcer=previous.get("enforcer"),
                        currentEnforcer="human",
                        baseRevision=context.base_revision,
                    )
                )
    return findings or [_finding("CHG001", "PASS", ".", "Project policy introduces no material architecture change relative to the base revision.", baseRevision=context.base_revision)]


def _rule_reviews_valid(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    seen: set[str] = set()
    known_rules = set(context.catalog)
    authorities = {item["id"]: item for item in context.authorities["authorities"]}
    today = date.today()
    for review in context.reviews:
        review_id = review["id"]
        if review_id in seen:
            results.append(_finding("REV001", "FAIL", _display_path(context, context.review_path), "Review id is duplicated.", review=review_id))
            continue
        seen.add(review_id)
        if review["rule"] not in known_rules or review["rule"] == "REV001":
            results.append(_finding("REV001", "FAIL", review["scope"], "Review references an unknown or non-reviewable rule.", review=review_id, reviewedRule=review["rule"]))
        elif review.get("ruleDigest") != context.catalog[review["rule"]]["ruleDigest"]:
            results.append(
                _finding(
                    "REV001",
                    "REVIEW_REQUIRED",
                    review["scope"],
                    "Review was accepted under different or unspecified rule semantics and cannot be applied.",
                    review=review_id,
                    staleRuleDigest=True,
                    recordedRuleDigest=review.get("ruleDigest"),
                    currentRuleDigest=context.catalog[review["rule"]]["ruleDigest"],
                )
            )
        authority = authorities.get(review["authorityId"])
        if authority is None:
            results.append(_finding("REV001", "FAIL", review["scope"], "Review references an unknown authority.", review=review_id, authorityId=review["authorityId"]))
        else:
            unknown_reviewers = sorted(set(review["reviewedBy"]) - set(authority["principals"]))
            if unknown_reviewers:
                results.append(_finding("REV001", "FAIL", review["scope"], "Review was attributed to principals outside the declared authority.", review=review_id, unknownReviewers=unknown_reviewers))
            if not any(_scope_matches(scope, review["scope"]) for scope in authority["protectedScopes"]):
                results.append(_finding("REV001", "FAIL", review["scope"], "Declared authority does not cover the reviewed scope.", review=review_id, authorityId=review["authorityId"]))
        enforcement = context.authorities["enforcement"]
        authority_mode = enforcement.get("mode", "team")
        approval_evidence = review["approvalEvidence"]
        if enforcement["provider"] == "github" and authority_mode == "team" and not approval_evidence.startswith("github-pr-review:"):
            results.append(_finding("REV001", "FAIL", review["scope"], "Team-mode GitHub review requires github-pr-review approval evidence.", review=review_id, approvalEvidence=approval_evidence))
        if enforcement["provider"] == "github" and authority_mode == "solo-maintainer":
            prefix = "github-maintainer-attestation:"
            evidence_url = approval_evidence.removeprefix(prefix)
            if not approval_evidence.startswith(prefix) or not evidence_url.startswith("https://github.com/") or any(character.isspace() for character in evidence_url):
                results.append(_finding("REV001", "FAIL", review["scope"], "Solo-maintainer GitHub review requires a github-maintainer-attestation with a GitHub evidence URL.", review=review_id, approvalEvidence=approval_evidence))
        revision = review["reviewedAtRevision"]
        if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
            results.append(_finding("REV001", "FAIL", review["scope"], "reviewedAtRevision must be a full 40-character Git commit SHA.", review=review_id, reviewedAtRevision=revision))
        else:
            try:
                subprocess.run(["git", "cat-file", "-e", f"{revision}^{{commit}}"], cwd=context.root, check=True, capture_output=True)
                ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", revision, "HEAD"], cwd=context.root, capture_output=True).returncode == 0
            except (OSError, subprocess.CalledProcessError):
                ancestor = False
            if not ancestor:
                results.append(_finding("REV001", "FAIL", review["scope"], "reviewedAtRevision is not a reachable ancestor of the current repository revision.", review=review_id, reviewedAtRevision=revision))
        missing = _references_resolve(context, review["authorizedBy"])
        if missing:
            results.append(_finding("REV001", "FAIL", review["scope"], "Review authority reference does not exist.", review=review_id, missing=missing))
        expiry = review.get("expiresOn")
        if expiry:
            try:
                if date.fromisoformat(expiry) < today:
                    results.append(_finding("REV001", "FAIL", review["scope"], "Review acknowledgement has expired.", review=review_id, expiresOn=expiry))
            except ValueError:
                results.append(_finding("REV001", "FAIL", review["scope"], "Review expiry is not an ISO date.", review=review_id, expiresOn=expiry))
    return results or [_finding("REV001", "PASS", _display_path(context, context.review_path), "Architecture review acknowledgements are structurally valid.", count=len(context.reviews))]


def _codeowners_entries(content: str) -> tuple[list[dict[str, object]], list[int]]:
    entries: list[dict[str, object]] = []
    invalid_lines: list[int] = []
    for line_number, raw in enumerate(content.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 2 or any(character in parts[0] for character in ("!", "[", "]")):
            invalid_lines.append(line_number)
            continue
        entries.append({"pattern": parts[0], "owners": set(parts[1:]), "line": line_number})
    return entries, invalid_lines


def _normalized_governed_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    if normalized in ("", ".", "./", "/"):
        return "."
    return normalized.removeprefix("./").lstrip("/").rstrip("/")


def _normalized_codeowners_pattern(value: str) -> str:
    return value.strip().replace("\\", "/").lstrip("/")


def _codeowners_pattern_covers_scope(pattern: str, scope: str) -> bool:
    value = _normalized_codeowners_pattern(pattern)
    governed = _normalized_governed_path(scope)
    if value in ("*", "**", "**/*"):
        return True
    if governed == ".":
        return False
    value = value.rstrip("/")
    if not any(character in value for character in "*?"):
        return value == governed
    for suffix in ("/**", "/**/*"):
        if value.endswith(suffix):
            prefix = value.removesuffix(suffix).rstrip("/")
            return prefix == governed
    return False


def _codeowners_pattern_targets_scope(pattern: str, scope: str) -> bool:
    governed = _normalized_governed_path(scope)
    if governed == ".":
        return True
    value = _normalized_codeowners_pattern(pattern).rstrip("/")
    static_prefix = re.split(r"[*?]", value, maxsplit=1)[0].rstrip("/")
    if not static_prefix:
        return True
    return (
        static_prefix == governed
        or static_prefix.startswith(governed + "/")
        or governed.startswith(static_prefix + "/")
    )


def _rule_authorities_valid(context: ValidationContext) -> list[Finding]:
    findings: list[Finding] = []
    verified_coverage: list[dict[str, object]] = []
    authorities = context.authorities["authorities"]
    ids = [item["id"] for item in authorities]
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        findings.append(_finding("AUT001", "FAIL", _display_path(context, context.authority_path), "Authority ids are duplicated.", duplicates=duplicates))
    enforcement = context.authorities["enforcement"]
    authority_mode = enforcement.get("mode", "team")
    if authority_mode == "solo-maintainer":
        required = {"pull-request", "no-direct-push", "required-status-checks"}
        incompatible = sorted({"code-owner-review", "dismiss-stale-reviews"} & set(enforcement["requirements"]))
        if incompatible:
            findings.append(_finding("AUT001", "FAIL", _display_path(context, context.authority_path), "Solo-maintainer governance declares team-only review controls that its sole principal cannot satisfy.", incompatibleRequirements=incompatible))
        unique_principals = sorted({principal for item in authorities for principal in item["principals"]})
        if len(unique_principals) != 1:
            findings.append(_finding("AUT001", "FAIL", _display_path(context, context.authority_path), "Solo-maintainer governance requires exactly one unique authority principal.", principals=unique_principals))
    else:
        required = {"pull-request", "code-owner-review", "dismiss-stale-reviews", "no-direct-push", "required-status-checks"}
    missing_requirements = sorted(required - set(enforcement["requirements"]))
    if missing_requirements:
        findings.append(_finding("AUT001", "FAIL", _display_path(context, context.authority_path), "Repository governance omits required anti-self-approval controls.", missingRequirements=missing_requirements))
    codeowners_path = _repo_path(context, enforcement["codeOwnersFile"])
    if not codeowners_path.is_file():
        findings.append(_finding("AUT001", "FAIL", enforcement["codeOwnersFile"], "Declared CODEOWNERS file does not exist."))
    else:
        entries, invalid_lines = _codeowners_entries(codeowners_path.read_text(encoding="utf-8"))
        if invalid_lines:
            findings.append(
                _finding(
                    "AUT001",
                    "FAIL",
                    enforcement["codeOwnersFile"],
                    "CODEOWNERS contains unsupported or ownerless patterns.",
                    invalidLines=invalid_lines,
                )
            )
        tokens = {token for entry in entries for token in entry["owners"]}
        missing_principals = sorted({principal for item in authorities for principal in item["principals"] if principal not in tokens})
        if missing_principals:
            findings.append(_finding("AUT001", "FAIL", enforcement["codeOwnersFile"], "Declared authority principals are absent from CODEOWNERS.", missingPrincipals=missing_principals))
        missing_coverage: list[dict[str, object]] = []
        unsafe_overrides: list[dict[str, object]] = []
        for authority in authorities:
            principals = set(authority["principals"])
            for scope in authority["protectedScopes"]:
                covering = [
                    entry
                    for entry in entries
                    if _codeowners_pattern_covers_scope(str(entry["pattern"]), scope)
                    and principals.issubset(entry["owners"])
                ]
                if not covering:
                    missing_coverage.append({
                        "authorityId": authority["id"],
                        "scope": scope,
                        "requiredPrincipals": sorted(principals),
                    })
                    continue
                overrides = [
                    entry
                    for entry in entries
                    if _codeowners_pattern_targets_scope(str(entry["pattern"]), scope)
                    and not principals.issubset(entry["owners"])
                ]
                if overrides:
                    unsafe_overrides.extend({
                        "authorityId": authority["id"],
                        "scope": scope,
                        "pattern": entry["pattern"],
                        "line": entry["line"],
                        "owners": sorted(entry["owners"]),
                    } for entry in overrides)
                else:
                    verified_coverage.append({
                        "authorityId": authority["id"],
                        "scope": scope,
                        "patterns": [entry["pattern"] for entry in covering],
                    })
        if missing_coverage:
            findings.append(
                _finding(
                    "AUT001",
                    "FAIL",
                    enforcement["codeOwnersFile"],
                    "Declared protected scopes are not covered by CODEOWNERS patterns owned by their authority principals.",
                    missingCoverage=missing_coverage,
                )
            )
        if unsafe_overrides:
            findings.append(
                _finding(
                    "AUT001",
                    "FAIL",
                    enforcement["codeOwnersFile"],
                    "CODEOWNERS contains narrower patterns that remove an authority from its protected scope.",
                    unsafeOverrides=unsafe_overrides,
                )
            )
    return findings or [_finding("AUT001", "PASS", _display_path(context, context.authority_path), "Every declared protected scope is covered by CODEOWNERS principals and the selected authority mode is internally consistent; platform enforcement remains external evidence.", authorityMode=authority_mode, authorities=ids, protectedBranches=enforcement["protectedBranches"], coverage=verified_coverage)]


def _rule_document_references(context: ValidationContext) -> list[Finding]:
    violations: list[Finding] = []
    module_reference_count = 0
    file_name = context.policy["moduleContract"]["fileName"]
    for module in context.policy["modules"]:
        contract_path = f"{module['root']}/{file_name}"
        contract = context.contracts.get(contract_path, {})
        for field in ("invariants", "architecture_decisions"):
            references = contract.get(field, [])
            if not isinstance(references, list):
                continue
            for reference in references:
                module_reference_count += 1
                document, separator, anchor = str(reference).partition("#")
                target = _repo_path(context, document)
                if not target.is_file():
                    violations.append(
                        _finding(
                            "DOC001",
                            "FAIL",
                            contract_path,
                            "Module contract references a missing document.",
                            reference=reference,
                        )
                    )
                elif separator and not any(
                    item["anchor"] == anchor.casefold()
                    for item in markdown_sections(target.read_text(encoding="utf-8"))
                ):
                    violations.append(
                        _finding(
                            "DOC001",
                            "FAIL",
                            contract_path,
                            "Module contract references a missing Markdown heading.",
                            reference=reference,
                        )
                    )

    catalog_references: dict[str, list[str]] = {}
    for rule_id, definition in context.catalog.items():
        reference = definition["reference"]
        document, anchor = split_reference(reference)
        catalog_references.setdefault(reference, []).append(rule_id)
        try:
            _, section = reference_section(context.root, reference)
        except (FileNotFoundError, ValueError):
            section = None
        if anchor is None or section is None:
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    "package:data/rules.json",
                    "Rule catalog reference does not resolve to a Markdown heading.",
                    catalogRule=rule_id,
                    reference=reference,
                )
            )
    for reference, rule_ids in catalog_references.items():
        if len(rule_ids) != 1:
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    reference,
                    "A validator-rule heading must be owned by exactly one catalog rule.",
                    catalogRules=rule_ids,
                )
            )

    normative_documents = context.norms.get("documents", [])
    if context.norms.get("version") != 1 or not isinstance(normative_documents, list):
        violations.append(
            _finding(
                "DOC001",
                "FAIL",
                "package:data/norms/index.json",
                "Normative index must declare version 1 and a document list.",
            )
        )
        normative_documents = []
    classified_references: set[str] = set()
    classifications: dict[str, str] = {}
    classified_heading_count = 0
    for document in normative_documents:
        reference = document.get("reference")
        enforcer = document.get("enforcer")
        if not isinstance(reference, str) or enforcer not in {"agent", "validator", "human"}:
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    "package:data/norms/index.json",
                    "Normative document classification is invalid.",
                    document=document,
                )
            )
            continue
        if reference in classified_references:
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    reference,
                    "Normative document is classified more than once.",
                )
            )
            continue
        classified_references.add(reference)
        classifications[reference] = enforcer
        missing_decisions = _references_resolve(context, document.get("decisionRefs", []))
        if missing_decisions:
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    reference,
                    "Normative classification references a missing decision.",
                    missing=missing_decisions,
                )
            )
        try:
            document_name, text = read_reference_document(context.root, reference)
        except (FileNotFoundError, ValueError):
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    reference,
                    "Classified normative document does not resolve.",
                )
            )
            continue
        classified_heading_count += sum(
            1 for item in markdown_sections(text) if item["level"] == 2
        )
        if enforcer == "human" and re.search(
            r"\b(?:must|must not|should|should not)\b",
            text,
            flags=re.IGNORECASE,
        ):
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    reference,
                    "Human guidance contains normative requirement language.",
                )
            )
        if enforcer != "validator":
            continue
        heading_references = {
            split_reference(rule["reference"])[1]: rule_id
            for rule_id, rule in context.catalog.items()
            if split_reference(rule["reference"])[0] == document_name
        }
        for section in (item for item in markdown_sections(text) if item["level"] == 2):
            if section["anchor"] not in heading_references:
                violations.append(
                    _finding(
                        "DOC001",
                        "FAIL",
                        f"{reference}#{section['anchor']}",
                        "Validator-enforced normative heading is not referenced by a catalog rule.",
                        heading=section["title"],
                    )
                )
        for anchor, rule_id in heading_references.items():
            matches = [
                item for item in markdown_sections(text)
                if item["level"] == 2 and item["anchor"] == anchor
            ]
            if len(matches) != 1:
                violations.append(
                    _finding(
                        "DOC001",
                        "FAIL",
                        f"{reference}#{anchor}",
                        "Catalog rule must resolve to exactly one validator-rule heading.",
                        catalogRule=rule_id,
                        matches=len(matches),
                    )
                )
    catalog_documents = {
        split_reference(rule["reference"])[0]
        for rule in context.catalog.values()
    }
    for reference in sorted(catalog_documents):
        if classifications.get(reference) != "validator":
            violations.append(
                _finding(
                    "DOC001",
                    "FAIL",
                    reference,
                    "Every catalog rule document must be explicitly classified as validator-enforced.",
                    observedEnforcer=classifications.get(reference),
                )
            )
    if "agent" not in classifications.values():
        violations.append(
            _finding(
                "DOC001",
                "FAIL",
                "package:data/norms/index.json",
                "Normative index does not declare a preventive agent core.",
            )
        )
    return violations or [
        _finding(
            "DOC001",
            "PASS",
            ".",
            "Normative, invariant, and architecture-decision references resolve.",
            catalogReferences=len(catalog_references),
            normativeDocuments=len(normative_documents),
            classifiedHeadings=classified_heading_count,
            moduleReferences=module_reference_count,
        )
    ]


def _rule_waivers_valid(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    known_rules = set(context.catalog)
    today = date.today()
    seen: set[str] = set()
    for waiver in context.waivers:
        waiver_id = waiver["id"]
        if waiver_id in seen:
            results.append(_finding("WVR001", "FAIL", _display_path(context, context.waiver_path), "Waiver id is duplicated.", waiver=waiver_id))
            continue
        seen.add(waiver_id)
        if waiver["rule"] not in known_rules or waiver["rule"] in ("WVR001", "REV001"):
            results.append(_finding("WVR001", "FAIL", waiver["scope"], "Waiver references an unknown or non-waivable rule.", waiver=waiver_id, rule=waiver["rule"]))
        elif waiver.get("ruleDigest") != context.catalog[waiver["rule"]]["ruleDigest"]:
            results.append(
                _finding(
                    "WVR001",
                    "REVIEW_REQUIRED",
                    waiver["scope"],
                    "Waiver was granted under different or unspecified rule semantics and cannot be applied.",
                    waiver=waiver_id,
                    staleRuleDigest=True,
                    recordedRuleDigest=waiver.get("ruleDigest"),
                    currentRuleDigest=context.catalog[waiver["rule"]]["ruleDigest"],
                )
            )
        try:
            scope_exists = _repo_path(context, waiver["scope"]).exists()
        except ValueError:
            scope_exists = False
        if not scope_exists:
            results.append(_finding("WVR001", "FAIL", waiver["scope"], "Waiver scope does not resolve inside the repository.", waiver=waiver_id))
        owned_roots = [item["root"].rstrip("/") for item in context.policy["modules"] + context.policy["hosts"]]
        covered = [root for root in owned_roots if root == waiver["scope"].rstrip("/") or root.startswith(waiver["scope"].rstrip("/") + "/")]
        if waiver["scope"].rstrip("/") in ("", ".") or len(covered) > 1:
            results.append(_finding("WVR001", "REVIEW_REQUIRED", waiver["scope"], "Waiver scope spans the repository or multiple ownership boundaries; justify why a narrower scope is impossible.", waiver=waiver_id, coveredRoots=covered))
        expiry = waiver.get("expiresOn")
        if expiry:
            try:
                expired = date.fromisoformat(expiry) < today
            except ValueError:
                results.append(_finding("WVR001", "FAIL", waiver["scope"], "Waiver expiry is not an ISO date.", waiver=waiver_id, expiresOn=expiry))
            else:
                if expired:
                    results.append(_finding("WVR001", "FAIL", waiver["scope"], "Waiver has expired.", waiver=waiver_id, expiresOn=expiry))
        for authority in waiver["authorizedBy"]:
            if not _repo_path(context, authority).is_file():
                results.append(_finding("WVR001", "FAIL", waiver["scope"], "Waiver authority does not exist.", waiver=waiver_id, authority=authority))
    return results or [_finding("WVR001", "PASS", _display_path(context, context.waiver_path), "All architecture waivers are valid.", count=len(context.waivers))]


EVALUATORS: dict[str, Callable[[ValidationContext], list[Finding]]] = {
    "policy_valid": _rule_policy_valid,
    "architecture_matches": _rule_architecture_matches,
    "module_contract": _rule_module_contract,
    "module_identity": _rule_module_identity,
    "functional_modules": _rule_functional_modules,
    "feature_ownership": _rule_feature_ownership,
    "hosts_are_adapters": _rule_hosts_are_adapters,
    "modules_do_not_depend_on_hosts": _rule_modules_do_not_depend_on_hosts,
    "cross_module_contracts": _rule_cross_module_contracts,
    "allowed_dependencies": _rule_allowed_dependencies,
    "policy_growth": _rule_policy_growth,
    "data_ownership": _rule_data_ownership,
    "no_speculative_structure": _rule_no_speculative_structure,
    "document_references": _rule_document_references,
    "waivers_valid": _rule_waivers_valid,
    "reviews_valid": _rule_reviews_valid,
    "authorities_valid": _rule_authorities_valid,
}


def _scope_matches(waiver_scope: str, finding_scope: str) -> bool:
    normalized_waiver = waiver_scope.rstrip("/") or "."
    normalized_finding = finding_scope.rstrip("/") or "."
    if normalized_waiver == ".":
        return True
    return normalized_finding == normalized_waiver or normalized_finding.startswith(normalized_waiver + "/")


def _review_fingerprint(finding: Finding) -> str:
    subject = {
        "rule": finding.rule,
        "ruleDigest": finding.rule_digest,
        "scope": finding.scope,
        "message": finding.message,
        "evidence": finding.evidence,
    }
    return hashlib.sha256(json.dumps(subject, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def evaluate(context: ValidationContext) -> list[Finding]:
    findings: list[Finding] = []
    for rule_id, definition in context.catalog.items():
        evaluator_name = definition["evaluator"]
        evaluator = EVALUATORS.get(evaluator_name)
        if evaluator is None:
            raise ValueError(f"Rule {rule_id} references unknown evaluator '{evaluator_name}'.")
        produced = evaluator(context)
        if any(finding.rule != rule_id for finding in produced):
            raise ValueError(f"Evaluator '{evaluator_name}' emitted a result for the wrong rule.")
        findings.extend(produced)

    def attach_rule_metadata(finding: Finding) -> None:
        definition = context.catalog[finding.rule]
        finding.reference = definition["reference"]
        finding.rule_digest = definition["ruleDigest"]

    for finding in findings:
        attach_rule_metadata(finding)

    invalid_waiver_ids = {
        str(finding.evidence.get("waiver"))
        for finding in findings
        if finding.rule == "WVR001" and finding.status == "FAIL" and finding.evidence.get("waiver")
    }
    stale_waiver_ids = {
        str(finding.evidence.get("waiver"))
        for finding in findings
        if finding.rule == "WVR001"
        and finding.evidence.get("staleRuleDigest")
        and finding.evidence.get("waiver")
    }
    matched: Counter[str] = Counter()
    for finding in findings:
        if finding.rule == "WVR001" or finding.status not in ("FAIL", "REVIEW_REQUIRED"):
            continue
        for waiver in context.waivers:
            if waiver["id"] in invalid_waiver_ids or waiver["id"] in stale_waiver_ids:
                continue
            if waiver["rule"] == finding.rule and _scope_matches(waiver["scope"], finding.scope):
                finding.status = "WAIVED"
                finding.waiver = waiver["id"]
                finding.message = f"{finding.message} Authorized waiver: {waiver['decision']}"
                matched[waiver["id"]] += 1
                break

    for waiver in context.waivers:
        if (
            waiver["id"] not in invalid_waiver_ids
            and waiver["id"] not in stale_waiver_ids
            and matched[waiver["id"]] == 0
        ):
            findings.append(
                _finding(
                    "WVR001",
                    "REVIEW_REQUIRED",
                    waiver["scope"],
                    "Valid waiver did not match any current violation; review whether it should be removed.",
                    waiver=waiver["id"],
                )
            )
    valid_review_ids = {
        review["id"]
        for review in context.reviews
        if not any(
            finding.rule == "REV001"
            and finding.status in ("FAIL", "REVIEW_REQUIRED")
            and finding.evidence.get("review") == review["id"]
            for finding in findings
        )
    }
    matched_reviews: Counter[str] = Counter()
    for finding in findings:
        if finding.status != "REVIEW_REQUIRED" or finding.rule == "REV001":
            continue
        finding.review_fingerprint = _review_fingerprint(finding)
        for review in context.reviews:
            if review["id"] not in valid_review_ids:
                continue
            if (
                review["rule"] == finding.rule
                and review.get("ruleDigest") == finding.rule_digest
                and review["scope"].rstrip("/") == finding.scope.rstrip("/")
                and review["subjectFingerprint"] == finding.review_fingerprint
            ):
                finding.status = "REVIEWED"
                finding.review = review["id"]
                finding.message = f"{finding.message} Accepted review: {review['decision']}"
                matched_reviews[review["id"]] += 1
                break
    for review in context.reviews:
        if review["id"] in valid_review_ids and matched_reviews[review["id"]] == 0:
            reviewed_rule_findings = [
                finding for finding in findings
                if finding.rule == review["rule"]
            ]
            if reviewed_rule_findings and all(
                finding.status == "NOT_APPLICABLE"
                for finding in reviewed_rule_findings
            ):
                continue
            findings.append(
                _finding(
                    "REV001",
                    "REVIEW_REQUIRED",
                    review["scope"],
                    "Review acknowledgement is stale or no longer matches a current semantic finding; refresh or remove it.",
                    review=review["id"],
                    reviewedRule=review["rule"],
                )
            )
    for finding in findings:
        attach_rule_metadata(finding)
    return findings
