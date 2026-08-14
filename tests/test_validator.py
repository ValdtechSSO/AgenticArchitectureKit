from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agentic_architecture_kit import __version__  # noqa: E402
from agentic_architecture_kit.contracts import ContractError, load_yaml_subset  # noqa: E402
from agentic_architecture_kit.context import locate, references, write_index  # noqa: E402
from agentic_architecture_kit.init_cli import export_payload, initialize  # noqa: E402
from agentic_architecture_kit.validate_cli import run  # noqa: E402


class ArchitectureValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        module = self.root / "src/Modules/Orders"
        features = module / "Features/OrderLifecycle"
        host = self.root / "src/Hosts/Cli"
        features.mkdir(parents=True)
        host.mkdir(parents=True)
        (module / "AGENTS.md").write_text("# Orders\n", encoding="utf-8")
        (module / "module.contract.yml").write_text(
            """id: orders
name: Orders
purpose: Manages current orders.
intent:
  aliases:
    - orders
ownership:
  domain: orders
  authoritative_data: []
risk:
  default: medium
  reasons: []
invariants:
  - domain/orders.md#identity
architecture_decisions:
  - architecture/decisions/ADR-001-orders.md
""",
            encoding="utf-8",
        )
        (features / "CreateOrder.cs").write_text("namespace Example.Orders;\n", encoding="utf-8")
        (module / "Orders.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Orders</AssemblyName></PropertyGroup></Project>\n',
            encoding="utf-8",
        )
        (host / "Program.cs").write_text("namespace Example.Cli;\n", encoding="utf-8")
        (host / "Cli.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>example</AssemblyName></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../../Modules/Orders/Orders.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        (self.root / "domain").mkdir()
        (self.root / "domain/orders.md").write_text("# Orders\n\n## Identity\n", encoding="utf-8")
        (self.root / "architecture/decisions").mkdir(parents=True)
        (self.root / "architecture/decisions/ADR-001-orders.md").write_text("# Orders decision\n", encoding="utf-8")

        self.policy = {
            "$schema": "https://raw.githubusercontent.com/OWNER/AgenticArchitectureKit/v0.3.0/src/agentic_architecture_kit/data/schemas/architecture-policy.schema.json",
            "version": 1,
            "project": "example",
            "adapter": "dotnet",
            "roots": {"modules": "src/Modules", "hosts": "src/Hosts"},
            "projectSearchRoots": ["src"],
            "structureSearchRoots": ["src"],
            "moduleContract": {
                "fileName": "module.contract.yml",
                "schema": "package:module-contract.schema.json",
                "forbiddenStructuralFields": ["paths", "handlers"],
            },
            "technicalModuleNames": ["Git", "Providers", "Validation"],
            "forbiddenDirectoryNames": ["Services", "Helpers", "Common"],
            "modules": [
                {
                    "id": "orders",
                    "root": "src/Modules/Orders",
                    "featureRoot": "src/Modules/Orders/Features",
                    "featureAreas": ["OrderLifecycle"],
                    "namespacePatterns": ["Example.Orders", "Example.Orders.*"],
                }
            ],
            "hosts": [
                {
                    "id": "cli",
                    "root": "src/Hosts/Cli",
                    "allowedSourcePatterns": ["Program.cs"],
                    "namespacePatterns": ["Example.Cli", "Example.Cli.*"],
                }
            ],
            "projects": [
                {
                    "path": "src/Modules/Orders/Orders.csproj",
                    "name": "Example.Orders",
                    "owner": {"kind": "module", "id": "orders"},
                    "role": "application",
                },
                {
                    "path": "src/Hosts/Cli/Cli.csproj",
                    "name": "example",
                    "owner": {"kind": "host", "id": "cli"},
                    "role": "host",
                },
            ],
            "allowedProjectDependencies": [
                {
                    "from": "src/Hosts/Cli/Cli.csproj",
                    "to": "src/Modules/Orders/Orders.csproj",
                }
            ],
            "dependencyRules": [],
        }
        self.policy_path = self.root / ".agentic/policies/architecture/project-policy.json"
        self.waiver_path = self.root / ".agentic/policies/architecture/waivers.json"
        self.review_path = self.root / ".agentic/policies/architecture/reviews.json"
        self.authority_path = self.root / ".agentic/policies/architecture/authorities.json"
        self.toolchain_path = self.root / ".agentic/toolchain.json"
        self.policy_path.parent.mkdir(parents=True)
        self.toolchain_path.write_text(json.dumps({
            "version": 1,
            "distribution": "agentic-architecture-kit",
            "toolVersion": __version__,
            "catalogVersion": 1,
            "extensions": [],
        }), encoding="utf-8")
        self._write_policy()
        self._write_waivers([])
        self._write_reviews([])
        self._write_authorities()
        (self.root / ".github").mkdir()
        (self.root / ".github/CODEOWNERS").write_text("* @test-owner\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Validator Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline"],
            cwd=self.root,
            check=True,
        )
        self.initial_revision = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout.strip()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_policy(self) -> None:
        self.policy_path.write_text(json.dumps(self.policy), encoding="utf-8")

    def _write_waivers(self, waivers: list[dict]) -> None:
        self.waiver_path.write_text(
            json.dumps({"version": 1, "waivers": waivers}), encoding="utf-8"
        )

    def _write_reviews(self, reviews: list[dict]) -> None:
        self.review_path.write_text(
            json.dumps({"version": 1, "reviews": reviews}), encoding="utf-8"
        )

    def _write_authorities(self) -> None:
        self.authority_path.write_text(json.dumps({
            "version": 1,
            "enforcement": {
                "provider": "github",
                "codeOwnersFile": ".github/CODEOWNERS",
                "protectedBranches": ["main"],
                "requirements": [
                    "pull-request", "code-owner-review", "dismiss-stale-reviews",
                    "no-direct-push", "required-status-checks",
                ],
            },
            "authorities": [{
                "id": "test-owner",
                "displayName": "Test architecture owner",
                "principals": ["@test-owner"],
                "protectedScopes": ["."],
            }],
        }), encoding="utf-8")

    def _run(self, *arguments: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = run(
                [
                    "--root",
                    str(self.root),
                    *arguments,
                ]
            )
        return code, stdout.getvalue(), stderr.getvalue()

    def test_valid_repository_has_no_failures(self) -> None:
        code, output, error = self._run("--format", "json")
        self.assertEqual(0, code, error)
        report = json.loads(output)
        self.assertEqual(0, report["summary"]["FAIL"])
        self.assertGreater(report["summary"]["PASS"], 0)
        self.assertGreater(report["summary"]["REVIEW_REQUIRED"], 0)
        for field in (
            "policyDigest", "waiverDigest", "reviewDigest", "authorityDigest",
            "toolchainDigest", "catalogDigest", "observedDigest",
        ):
            self.assertTrue(report[field].startswith("sha256:"), field)

    def test_tool_version_must_match_the_project_pin(self) -> None:
        toolchain = json.loads(self.toolchain_path.read_text(encoding="utf-8"))
        toolchain["toolVersion"] = "99.0.0"
        self.toolchain_path.write_text(json.dumps(toolchain), encoding="utf-8")
        code, _, error = self._run()
        self.assertEqual(2, code)
        self.assertIn("requires agentic-architecture-kit==99.0.0", error)

    def test_unapproved_project_dependency_fails(self) -> None:
        self.policy["allowedProjectDependencies"] = []
        self._write_policy()
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] DEP003 src/Hosts/Cli/Cli.csproj", output)

    def test_project_policy_cannot_weaken_module_to_host_rule(self) -> None:
        module_project = self.root / "src/Modules/Orders/Orders.csproj"
        module_project.write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Orders</AssemblyName></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../../Hosts/Cli/Cli.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        self.policy["allowedProjectDependencies"].append(
            {
                "from": "src/Modules/Orders/Orders.csproj",
                "to": "src/Hosts/Cli/Cli.csproj",
            }
        )
        self._write_policy()
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] DEP001 src/Modules/Orders/Orders.csproj", output)

    def test_valid_waiver_is_visible_and_allows_the_run(self) -> None:
        self.policy["allowedProjectDependencies"] = []
        self._write_policy()
        self._write_waivers(
            [
                {
                    "id": "EXAMPLE-ARCH-001",
                    "rule": "DEP003",
                    "scope": "src/Hosts/Cli/Cli.csproj",
                    "decision": "Allow the CLI dependency during migration.",
                    "reason": "The public application contract is being extracted.",
                    "risk": "The host remains coupled to the module implementation.",
                    "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
                    "reviewWhen": ["The CLI dependency changes"],
                }
            ]
        )
        code, output, error = self._run("--format", "json")
        self.assertEqual(0, code, error)
        report = json.loads(output)
        waived = [result for result in report["results"] if result["status"] == "WAIVED"]
        self.assertEqual("EXAMPLE-ARCH-001", waived[0]["waiver"])
        self.assertEqual("DEP003", waived[0]["rule"])

    def test_missing_document_anchor_is_a_failure(self) -> None:
        contract = self.root / "src/Modules/Orders/module.contract.yml"
        contract.write_text(contract.read_text(encoding="utf-8").replace("#identity", "#missing"), encoding="utf-8")
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] DOC001", output)

    def test_review_findings_can_be_promoted_to_a_gate(self) -> None:
        code, output, _ = self._run("--fail-on-review")
        self.assertEqual(1, code)
        self.assertIn("[REVIEW_REQUIRED] FEAT001", output)

    def test_fingerprint_bound_reviews_make_strict_review_gate_usable(self) -> None:
        _, output, error = self._run("--format", "json")
        self.assertFalse(error)
        report = json.loads(output)
        reviews = []
        for index, finding in enumerate(
            result for result in report["results"] if result["status"] == "REVIEW_REQUIRED"
        ):
            reviews.append({
                "id": f"TEST-REVIEW-{index}",
                "rule": finding["rule"],
                "scope": finding["scope"],
                "subjectFingerprint": finding["reviewFingerprint"],
                "decision": "Accepted for this exact test subject.",
                "authorityId": "test-owner",
                "reviewedBy": ["@test-owner"],
                "approvalEvidence": "github-pr-review:test-approved-review",
                "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
                "reviewedAtRevision": self.initial_revision,
                "reviewWhen": ["The subject fingerprint changes"],
            })
        self._write_reviews(reviews)

        code, output, error = self._run("--format", "json", "--fail-on-review")
        self.assertEqual(0, code, error)
        reviewed = [item for item in json.loads(output)["results"] if item["status"] == "REVIEWED"]
        self.assertEqual(len(reviews), len(reviewed))

        (self.root / "src/Modules/Orders/Features/CancelOrder").mkdir()
        self.policy["modules"][0]["featureAreas"].append("CancelOrder")
        self._write_policy()
        code, output, _ = self._run("--fail-on-review")
        self.assertEqual(1, code)
        self.assertIn("[REVIEW_REQUIRED] REV001", output)

    def test_review_revision_must_be_a_reachable_commit_and_authority_must_match(self) -> None:
        _, output, _ = self._run("--format", "json")
        finding = next(
            item for item in json.loads(output)["results"]
            if item["status"] == "REVIEW_REQUIRED"
        )
        self._write_reviews([{
            "id": "UNREACHABLE-REVIEW",
            "rule": finding["rule"],
            "scope": finding["scope"],
            "subjectFingerprint": finding["reviewFingerprint"],
            "decision": "This record must not be accepted.",
            "authorityId": "test-owner",
            "reviewedBy": ["@not-the-codeowner"],
            "approvalEvidence": "github-pr-review:test-invalid",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewedAtRevision": "0" * 40,
            "reviewWhen": ["The subject changes"],
        }])
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] REV001", output)

    def test_declared_authority_must_exist_in_codeowners(self) -> None:
        (self.root / ".github/CODEOWNERS").write_text("* @someone-else\n", encoding="utf-8")
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] AUT001", output)

    def test_source_import_detects_module_to_host_without_project_reference(self) -> None:
        source = self.root / "src/Modules/Orders/Features/OrderLifecycle/CreateOrder.cs"
        source.write_text(
            "using Example.Cli;\nnamespace Example.Orders.Features.OrderLifecycle;\n",
            encoding="utf-8",
        )
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] DEP001 src/Modules/Orders/Features/OrderLifecycle/CreateOrder.cs", output)

    def test_policy_growth_without_decision_reference_fails_against_git_base(self) -> None:
        self.policy["allowedProjectDependencies"].append({
            "from": "src/Modules/Orders/Orders.csproj",
            "to": "src/Hosts/Cli/Cli.csproj",
        })
        self._write_policy()

        code, output, _ = self._run("--base-ref", "HEAD")
        self.assertEqual(1, code)
        self.assertIn("[FAIL] CHG001", output)

    def test_dependency_selector_growth_emits_a_valid_review_finding(self) -> None:
        self.policy["dependencyRules"] = [{
            "from": {"ownerKind": "host"},
            "to": {"ownerKind": "module"},
            "decisionRefs": ["architecture/decisions/ADR-001-orders.md"],
        }]
        self._write_policy()
        code, output, error = self._run("--base-ref", "HEAD", "--format", "json")
        self.assertEqual(0, code, error)
        change = next(item for item in json.loads(output)["results"] if item["rule"] == "CHG001")
        self.assertEqual("REVIEW_REQUIRED", change["status"])
        self.assertEqual(".agentic/policies/architecture/project-policy.json", change["scope"])

    def test_scalable_dependency_rule_can_replace_exact_edge_allowlist(self) -> None:
        self.policy["allowedProjectDependencies"] = []
        self.policy["dependencyRules"] = [{
            "from": {"ownerKind": "host", "role": "host"},
            "to": {"ownerKind": "module", "role": "application"},
            "decisionRefs": ["architecture/decisions/ADR-001-orders.md"],
        }]
        self._write_policy()
        code, output, error = self._run()
        self.assertEqual(0, code, error)
        self.assertIn("[PASS] DEP003", output)

    def test_repository_wide_waiver_requires_scope_review(self) -> None:
        self.policy["allowedProjectDependencies"] = []
        self._write_policy()
        self._write_waivers([{
            "id": "BROAD-001",
            "rule": "DEP003",
            "scope": ".",
            "decision": "Temporary example only.",
            "reason": "Exercise broad-scope detection.",
            "risk": "Unrelated failures could be hidden.",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewWhen": ["A narrower scope becomes possible"],
        }])
        code, output, _ = self._run("--fail-on-review")
        self.assertEqual(1, code)
        self.assertIn("[WAIVED] DEP003", output)
        self.assertIn("[REVIEW_REQUIRED] WVR001 .", output)

    def test_context_index_and_retrieval_report_provenance(self) -> None:
        documents = write_index(self.root, self.policy)
        self.assertEqual({"repository", "modules", "projects", "dependencies", "documents", "tests"}, set(documents))
        self.assertTrue((self.root / ".agentic/generated/index/modules.json").is_file())
        located = locate(self.root, self.policy, "orders")
        self.assertEqual("declared", located["matches"][0]["provenance"])
        found = references(self.root, self.policy, "CreateOrder")
        self.assertEqual("observed", found["matches"][0]["provenance"])

    def test_task_evidence_is_retained_with_a_manifest(self) -> None:
        code, _, error = self._run("--task-id", "test-task")
        self.assertEqual(0, code, error)
        evidence = self.root / ".agentic/runtime/evidence/test-task" / self.initial_revision
        self.assertTrue((evidence / "architecture.json").is_file())
        self.assertTrue((evidence / "manifest.json").is_file())

    def test_yaml_subset_rejects_mapping_sequence_items(self) -> None:
        path = self.root / "invalid.yml"
        path.write_text("items:\n  - id: unsupported\n", encoding="utf-8")
        with self.assertRaises(ContractError):
            load_yaml_subset(path)

    def test_init_creates_only_project_owned_configuration(self) -> None:
        target = self.root / "initialized"
        target.mkdir()
        initialize(target, "@architecture-team")
        self.assertTrue((target / ".agentic/toolchain.json").is_file())
        self.assertTrue((target / ".agentic/policies/architecture/authorities.json").is_file())
        self.assertFalse((target / ".agentic/policies/architecture/project-policy.json").exists())
        self.assertFalse((target / "tools/architecture").exists())
        self.assertFalse((target / ".agentic/contracts").exists())

    def test_offline_export_is_explicit_and_contains_portable_assets(self) -> None:
        target = self.root / "offline"
        manifest = export_payload(target)
        exported = target / f"agentic-architecture-kit-{__version__}"
        self.assertTrue((exported / "agentic_architecture_kit/data/rules.json").is_file())
        self.assertTrue((exported / "agentic_architecture_kit/data/schemas/architecture-policy.schema.json").is_file())
        self.assertEqual(__version__, manifest["toolVersion"])


class ExampleRepositoryTests(unittest.TestCase):
    def _run_example(self, name: str) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = run([
                "--root", str(REPOSITORY_ROOT / "examples" / name),
            ])
        return code, output.getvalue()

    def test_valid_dotnet_example_has_no_architecture_failure(self) -> None:
        code, output = self._run_example("dotnet-valid")
        self.assertEqual(0, code, output)
        self.assertNotIn("[FAIL]", output)
        self.assertFalse((REPOSITORY_ROOT / "examples/dotnet-valid/.agentic/contracts").exists())

    def test_invalid_dotnet_example_demonstrates_source_dependency_failure(self) -> None:
        code, output = self._run_example("dotnet-invalid")
        self.assertEqual(1, code)
        self.assertIn("[FAIL] DEP001", output)

    def test_kit_self_validation_exercises_real_host_to_module_source_edges(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = run(["--root", str(REPOSITORY_ROOT), "--format", "json"])
        self.assertEqual(0, code)
        report = json.loads(output.getvalue())
        dependency = next(item for item in report["results"] if item["rule"] == "DEP003")
        self.assertEqual("PASS", dependency["status"])
        self.assertGreater(len(dependency["evidence"]["sourceDependencies"]), 0)
        self.assertEqual(
            {"host:aak-cli"},
            {item["from"] for item in dependency["evidence"]["sourceDependencies"]},
        )

    def test_distribution_version_pins_are_consistent(self) -> None:
        self.assertIn(f'version = "{__version__}"', (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        toolchains = [
            REPOSITORY_ROOT / ".agentic/toolchain.json",
            REPOSITORY_ROOT / "examples/dotnet-valid/.agentic/toolchain.json",
            REPOSITORY_ROOT / "examples/dotnet-invalid/.agentic/toolchain.json",
            REPOSITORY_ROOT / "src/agentic_architecture_kit/data/templates/project/toolchain.json",
        ]
        for path in toolchains:
            self.assertEqual(__version__, json.loads(path.read_text(encoding="utf-8"))["toolVersion"], str(path))
        release_schema_prefix = (
            f"https://raw.githubusercontent.com/ValdtechSSO/AgenticArchitectureKit/v{__version__}/"
        )
        for path in (
            REPOSITORY_ROOT / ".agentic/policies/architecture"
        ).glob("*.json"):
            document = json.loads(path.read_text(encoding="utf-8"))
            if "$schema" in document:
                self.assertTrue(document["$schema"].startswith(release_schema_prefix), str(path))


if __name__ == "__main__":
    unittest.main()
