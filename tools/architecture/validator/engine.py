from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from collections import Counter, deque
from datetime import date
from pathlib import Path
from typing import Callable

from .model import Finding, ValidationContext


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


def _namespace_owner(context: ValidationContext, namespace: str) -> tuple[str, str, bool] | None:
    for module in context.policy["modules"]:
        if any(fnmatch.fnmatchcase(namespace, pattern) for pattern in module.get("namespacePatterns", [])):
            is_contract = any(
                fnmatch.fnmatchcase(namespace, pattern)
                for pattern in module.get("contractNamespacePatterns", [])
            )
            return "module", module["id"], is_contract
    for host in context.policy["hosts"]:
        if any(fnmatch.fnmatchcase(namespace, pattern) for pattern in host.get("namespacePatterns", [])):
            return "host", host["id"], False
    return None


def _project_matches(declaration: dict, selector: dict) -> bool:
    owner = declaration["owner"]
    return (
        ("ownerKind" not in selector or selector["ownerKind"] == owner["kind"])
        and ("ownerId" not in selector or selector["ownerId"] == owner["id"])
        and ("role" not in selector or selector["role"] == declaration["role"])
        and ("pathPattern" not in selector or fnmatch.fnmatchcase(declaration["path"], selector["pathPattern"]))
    )


def _references_resolve(context: ValidationContext, references: list[str]) -> list[str]:
    return [reference for reference in references if not _repo_path(context, reference).is_file()]


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
                "Declared modules, hosts, and projects match the observed repository.",
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
        results.append(_finding("MOD001", "FAIL", context.policy["roots"]["modules"], "No module was observed."))
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
    return results


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


def _rule_modules_do_not_depend_on_hosts(context: ValidationContext) -> list[Finding]:
    projects = _declared_projects(context)
    graph = {project.path: project.references for project in context.observed.projects}
    module_projects = {
        path for path, item in projects.items() if item["owner"]["kind"] == "module"
    }
    host_projects = {
        path for path, item in projects.items() if item["owner"]["kind"] == "host"
    }
    violations: list[Finding] = []
    for project in sorted(module_projects):
        path = _dependency_path(graph, project, host_projects)
        if path:
            violations.append(
                _finding(
                    "DEP001",
                    "FAIL",
                    project,
                    "Module project depends on a host project.",
                    dependencyPath=path,
                )
            )
    for dependency in context.observed.source_dependencies:
        source = _namespace_owner(context, dependency.source_namespace)
        target = _namespace_owner(context, dependency.target_namespace)
        if source and target and source[0] == "module" and target[0] == "host":
            violations.append(
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
    return violations or [
        _finding("DEP001", "PASS", ".", "No module project depends on a host project.")
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
    unexpected = []
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
    if unexpected:
        return [
            _finding(
                "DEP003",
                "FAIL",
                source,
                "Observed project dependency is not allowed by project policy.",
                target=target,
            )
            for source, target in unexpected
        ]
    return [
        _finding(
            "DEP003",
            "PASS",
            ".",
            "Every observed project dependency is allowed by project policy.",
            dependencies=[{"from": source, "to": target} for source, target in sorted(actual)],
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
            "REVIEW_REQUIRED",
            ".",
            "Mechanical speculative-structure checks passed; necessity of existing boundaries requires review.",
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
            scope = item.get("root") or item.get("path") or item.get("from") or ".agentic/policies/architecture/project-policy.json"
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
    return findings or [_finding("CHG001", "PASS", ".", "Project policy introduces no material architecture change relative to the base revision.", baseRevision=context.base_revision)]


def _rule_reviews_valid(context: ValidationContext) -> list[Finding]:
    results: list[Finding] = []
    seen: set[str] = set()
    known_rules = set(context.catalog)
    today = date.today()
    for review in context.reviews:
        review_id = review["id"]
        if review_id in seen:
            results.append(_finding("REV001", "FAIL", _display_path(context, context.review_path), "Review id is duplicated.", review=review_id))
            continue
        seen.add(review_id)
        if review["rule"] not in known_rules or review["rule"] == "REV001":
            results.append(_finding("REV001", "FAIL", review["scope"], "Review references an unknown or non-reviewable rule.", review=review_id, reviewedRule=review["rule"]))
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


def _markdown_anchor_exists(path: Path, anchor: str) -> bool:
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = match.group(1).strip().casefold()
        heading = re.sub(r"[`*_~]", "", heading)
        slug = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
        slug = re.sub(r"[\s-]+", "-", slug).strip("-")
        if slug == anchor.casefold():
            return True
    return False


def _rule_document_references(context: ValidationContext) -> list[Finding]:
    violations: list[Finding] = []
    file_name = context.policy["moduleContract"]["fileName"]
    for module in context.policy["modules"]:
        contract_path = f"{module['root']}/{file_name}"
        contract = context.contracts.get(contract_path, {})
        for field in ("invariants", "architecture_decisions"):
            references = contract.get(field, [])
            if not isinstance(references, list):
                continue
            for reference in references:
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
                elif separator and not _markdown_anchor_exists(target, anchor):
                    violations.append(
                        _finding(
                            "DOC001",
                            "FAIL",
                            contract_path,
                            "Module contract references a missing Markdown heading.",
                            reference=reference,
                        )
                    )
    return violations or [
        _finding("DOC001", "PASS", ".", "Invariant and architecture-decision references resolve.")
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

    invalid_waiver_ids = {
        str(finding.evidence.get("waiver"))
        for finding in findings
        if finding.rule == "WVR001" and finding.status == "FAIL" and finding.evidence.get("waiver")
    }
    matched: Counter[str] = Counter()
    for finding in findings:
        if finding.rule == "WVR001" or finding.status not in ("FAIL", "REVIEW_REQUIRED"):
            continue
        for waiver in context.waivers:
            if waiver["id"] in invalid_waiver_ids:
                continue
            if waiver["rule"] == finding.rule and _scope_matches(waiver["scope"], finding.scope):
                finding.status = "WAIVED"
                finding.waiver = waiver["id"]
                finding.message = f"{finding.message} Authorized waiver: {waiver['decision']}"
                matched[waiver["id"]] += 1
                break

    for waiver in context.waivers:
        if waiver["id"] not in invalid_waiver_ids and matched[waiver["id"]] == 0:
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
            and finding.status == "FAIL"
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
    return findings
