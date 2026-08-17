from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agentic_architecture_kit import __version__  # noqa: E402
from agentic_architecture_kit.adopt_cli import adopt  # noqa: E402
from agentic_architecture_kit.cli import main as cli  # noqa: E402
from agentic_architecture_kit.contracts import ContractError, load_yaml_subset  # noqa: E402
from agentic_architecture_kit.context import locate, references, write_index  # noqa: E402
from agentic_architecture_kit.explain_cli import run as explain  # noqa: E402
from agentic_architecture_kit.engine import _rule_policy_growth  # noqa: E402
from agentic_architecture_kit.init_cli import export_payload, initialize  # noqa: E402
from agentic_architecture_kit.norms import compute_rule_digest  # noqa: E402
from agentic_architecture_kit.resources import read_json as read_bundled_json  # noqa: E402
from agentic_architecture_kit.resources import read_text as read_bundled_text  # noqa: E402
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
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>example</AssemblyName>'
            '<RootNamespace>Example.Cli</RootNamespace></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../../Modules/Orders/Orders.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        (self.root / "domain").mkdir()
        (self.root / "domain/orders.md").write_text("# Orders\n\n## Identity\n", encoding="utf-8")
        (self.root / "architecture/decisions").mkdir(parents=True)
        (self.root / "architecture/decisions/ADR-001-orders.md").write_text("# Orders decision\n", encoding="utf-8")

        self.policy = {
            "$schema": "https://raw.githubusercontent.com/OWNER/AgenticArchitectureKit/v0.4.6/src/agentic_architecture_kit/data/schemas/architecture-policy.schema.json",
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
            "catalogVersion": 2,
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
        self.rule_digests = {
            rule["id"]: compute_rule_digest(self.root, rule)
            for rule in read_bundled_json("data/rules.json")["rules"]
        }

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

    def _write_authorities(
        self,
        mode: str | None = None,
        principals: list[str] | None = None,
        requirements: list[str] | None = None,
    ) -> None:
        if requirements is None:
            requirements = (
                ["pull-request", "no-direct-push", "required-status-checks"]
                if mode == "solo-maintainer"
                else [
                    "pull-request", "code-owner-review", "dismiss-stale-reviews",
                    "no-direct-push", "required-status-checks",
                ]
            )
        enforcement = {
            "provider": "github",
            "codeOwnersFile": ".github/CODEOWNERS",
            "protectedBranches": ["main"],
            "requirements": requirements,
        }
        if mode is not None:
            enforcement["mode"] = mode
        self.authority_path.write_text(json.dumps({
            "version": 1,
            "enforcement": enforcement,
            "authorities": [{
                "id": "test-owner",
                "displayName": "Test architecture owner",
                "principals": principals or ["@test-owner"],
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
        self.assertTrue(all(item["reference"].startswith("package:") for item in report["results"]))
        self.assertTrue(all(item["ruleDigest"].startswith("sha256:") for item in report["results"]))
        documentation = next(item for item in report["results"] if item["rule"] == "DOC001")
        self.assertEqual(17, documentation["evidence"]["catalogReferences"])
        self.assertEqual(3, documentation["evidence"]["normativeDocuments"])
        self.assertEqual(0, report["summary"]["FAIL"])
        self.assertGreater(report["summary"]["PASS"], 0)
        self.assertGreater(report["summary"]["REVIEW_REQUIRED"], 0)
        for field in (
            "policyDigest", "waiverDigest", "reviewDigest", "authorityDigest",
            "toolchainDigest", "catalogDigest", "observedDigest",
        ):
            self.assertTrue(report[field].startswith("sha256:"), field)

    def test_invalid_policy_role_is_rejected_by_pol001_gate(self) -> None:
        self.policy["projects"][0]["role"] = "not-a-role"
        self._write_policy()
        code, _, error = self._run()
        self.assertEqual(2, code)
        self.assertIn("does not conform", error)

    def test_missing_module_router_fails_mod001(self) -> None:
        (self.root / "src/Modules/Orders/AGENTS.md").unlink()
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] MOD001", output)

    def test_wrong_module_contract_identity_fails_mod002(self) -> None:
        contract = self.root / "src/Modules/Orders/module.contract.yml"
        contract.write_text(
            contract.read_text(encoding="utf-8").replace("id: orders", "id: wrong"),
            encoding="utf-8",
        )
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] MOD002", output)

    def test_technical_module_name_fails_mod003(self) -> None:
        self.policy["technicalModuleNames"].append("Orders")
        self._write_policy()
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] MOD003", output)

    def test_undeclared_host_source_fails_host001(self) -> None:
        (self.root / "src/Hosts/Cli/Unexpected.cs").write_text(
            "namespace Example.Cli;\n",
            encoding="utf-8",
        )
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] HOST001", output)

    def test_explain_combines_rule_definition_with_repository_state(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = explain(["DEP003", "--root", str(self.root)])
        self.assertEqual(0, code)
        value = output.getvalue()
        self.assertIn("State: PASS", value)
        self.assertIn("Rule digest: sha256:", value)
        self.assertIn("Reference: package:data/norms/portable-rules.md#dep003", value)
        self.assertIn("Evidence:", value)

    def test_core_is_available_without_repository_validation(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli(["core"])
        self.assertEqual(0, code)
        self.assertIn("# Architecture decision core", output.getvalue())
        self.assertIn("## Reversal-cost rule", output.getvalue())

    def test_agent_operational_guides_are_available_without_the_source_repository(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli(["guide"])
        self.assertEqual(0, code)
        self.assertIn("adapter-development:", output.getvalue())
        self.assertIn("bootstrap:", output.getvalue())
        self.assertIn("github-governance:", output.getvalue())

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli(["guide", "bootstrap"])
        self.assertEqual(0, code)
        self.assertIn("# Creating or evolving a project", output.getvalue())
        self.assertIn("## 11. Later evolution", output.getvalue())
        self.assertIn("aak guide github-governance", output.getvalue())

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli(["guide", "github-governance"])
        self.assertEqual(0, code)
        self.assertIn("# GitHub authority enforcement", output.getvalue())
        self.assertIn("## Solo-maintainer mode", output.getvalue())

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli(["guide", "adapter-development"])
        self.assertEqual(0, code)
        self.assertIn("# Writing a technology adapter", output.getvalue())
        self.assertIn("## 7. Release checklist", output.getvalue())

        for relative in (
            "data/guides/adapter-development.md",
            "data/guides/bootstrap.md",
            "data/guides/github-governance.md",
        ):
            packaged = read_bundled_text(relative)
            self.assertNotIn("docs/", packaged)
            self.assertNotIn("../", packaged)

    def test_web_guides_cover_the_packaged_operational_sections(self) -> None:
        pairs = (
            ("data/guides/adapter-development.md", "docs/adapter-development.md"),
            ("data/guides/bootstrap.md", "docs/create-project-from-zero.md"),
            ("data/guides/github-governance.md", "docs/github-governance.md"),
        )
        for packaged_path, web_path in pairs:
            packaged = read_bundled_text(packaged_path)
            web = (REPOSITORY_ROOT / web_path).read_text(encoding="utf-8")
            packaged_sections = [line for line in packaged.splitlines() if line.startswith("## ")]
            web_sections = [line for line in web.splitlines() if line.startswith("## ")]
            self.assertEqual(packaged_sections, web_sections, web_path)

    def test_neutral_templates_are_discoverable_and_readable_through_the_cli(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli(["template"])
        self.assertEqual(0, code)
        self.assertIn("AGENTS.md", output.getvalue().splitlines())
        self.assertIn("github-architecture.yml", output.getvalue().splitlines())
        self.assertIn("module.contract.yml", output.getvalue().splitlines())

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli(["template", "AGENTS.md"])
        self.assertEqual(0, code)
        self.assertIn("# {ProjectName}", output.getvalue())
        self.assertIn("aak guide bootstrap", output.getvalue())

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

    def test_cross_module_implementation_dependency_fails_dep002(self) -> None:
        payments = self.root / "src/Modules/Payments"
        payments.mkdir()
        (payments / "AGENTS.md").write_text("# Payments\n", encoding="utf-8")
        (payments / "module.contract.yml").write_text(
            """id: payments
name: Payments
purpose: Manages current payments.
intent:
  aliases:
    - payments
ownership:
  domain: payments
  authoritative_data: []
risk:
  default: medium
  reasons: []
invariants:
  - domain/payments.md#identity
architecture_decisions:
  - architecture/decisions/ADR-002-payments.md
""",
            encoding="utf-8",
        )
        (payments / "Payments.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Payments</AssemblyName>'
            '</PropertyGroup></Project>\n',
            encoding="utf-8",
        )
        (payments / "Payment.cs").write_text("namespace Example.Payments;\n", encoding="utf-8")
        (self.root / "domain/payments.md").write_text("# Payments\n\n## Identity\n", encoding="utf-8")
        (self.root / "architecture/decisions/ADR-002-payments.md").write_text(
            "# Payments decision\n",
            encoding="utf-8",
        )
        orders_project = self.root / "src/Modules/Orders/Orders.csproj"
        orders_project.write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Orders</AssemblyName></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../Payments/Payments.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        self.policy["modules"].append({
            "id": "payments",
            "root": "src/Modules/Payments",
            "namespacePatterns": ["Example.Payments", "Example.Payments.*"],
        })
        self.policy["projects"].append({
            "path": "src/Modules/Payments/Payments.csproj",
            "name": "Example.Payments",
            "owner": {"kind": "module", "id": "payments"},
            "role": "application",
        })
        self.policy["allowedProjectDependencies"].append({
            "from": "src/Modules/Orders/Orders.csproj",
            "to": "src/Modules/Payments/Payments.csproj",
        })
        self._write_policy()

        code, output, _ = self._run()

        self.assertEqual(1, code)
        self.assertIn("[FAIL] DEP002 src/Modules/Orders/Orders.csproj", output)

    def test_forbidden_catch_all_directory_fails_str001(self) -> None:
        (self.root / "src/Modules/Orders/Helpers").mkdir()
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] STR001", output)

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

    def test_test_project_may_depend_on_and_import_a_host(self) -> None:
        test_root = self.root / "tests/EndToEnd/Cli"
        test_root.mkdir(parents=True)
        test_project = "tests/EndToEnd/Cli/Example.Cli.EndToEndTests.csproj"
        (self.root / test_project).write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Cli.EndToEndTests</AssemblyName>'
            '<IsTestProject>true</IsTestProject></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../../../src/Hosts/Cli/Cli.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        (test_root / "CliTests.cs").write_text(
            "using Example.Cli;\nnamespace Example.Orders.CliTests;\n",
            encoding="utf-8",
        )
        self.policy["projectSearchRoots"].append("tests")
        self.policy["projects"].append({
            "path": test_project,
            "name": "Example.Cli.EndToEndTests",
            "owner": {"kind": "module", "id": "orders"},
            "role": "test",
        })
        self.policy["allowedProjectDependencies"].append({
            "from": test_project,
            "to": "src/Hosts/Cli/Cli.csproj",
        })
        self._write_policy()

        code, output, error = self._run()

        self.assertEqual(0, code, error + output)
        self.assertNotIn("[FAIL] DEP001", output)

    def test_test_role_cannot_hide_a_production_module_dependency(self) -> None:
        module_project = self.root / "src/Modules/Orders/Orders.csproj"
        module_project.write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Orders</AssemblyName></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../../Hosts/Cli/Cli.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        self.policy["projects"][0]["role"] = "test"
        self.policy["allowedProjectDependencies"].append({
            "from": "src/Modules/Orders/Orders.csproj",
            "to": "src/Hosts/Cli/Cli.csproj",
        })
        self._write_policy()

        code, output, _ = self._run()

        self.assertEqual(1, code)
        self.assertIn("[FAIL] ARC001 src/Modules/Orders/Orders.csproj", output)
        self.assertIn("Declared test role does not match observed test-project evidence.", output)

    def test_valid_waiver_is_visible_and_allows_the_run(self) -> None:
        self.policy["allowedProjectDependencies"] = []
        self._write_policy()
        self._write_waivers(
            [
                {
                    "id": "EXAMPLE-ARCH-001",
                    "rule": "DEP003",
                    "ruleDigest": self.rule_digests["DEP003"],
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

    def test_stale_rule_digest_prevents_waiver_from_silencing_a_violation(self) -> None:
        self.policy["allowedProjectDependencies"] = []
        self._write_policy()
        self._write_waivers([{
            "id": "STALE-WAIVER",
            "rule": "DEP003",
            "ruleDigest": "sha256:" + "0" * 64,
            "scope": "src/Hosts/Cli/Cli.csproj",
            "decision": "Previously accepted migration.",
            "reason": "Exercise semantic invalidation.",
            "risk": "The dependency remains unapproved under current semantics.",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewWhen": ["The rule semantics change"],
        }])
        code, output, _ = self._run("--format", "json")
        self.assertEqual(1, code)
        results = json.loads(output)["results"]
        self.assertTrue(any(
            item["rule"] == "DEP003" and item["status"] == "FAIL"
            for item in results
        ))
        self.assertTrue(any(
            item["rule"] == "WVR001"
            and item["status"] == "REVIEW_REQUIRED"
            and item["evidence"].get("staleRuleDigest")
            for item in results
        ))

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
                "ruleDigest": finding["ruleDigest"],
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
            "ruleDigest": finding["ruleDigest"],
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

    def test_solo_maintainer_attestation_resolves_semantic_review(self) -> None:
        self._write_authorities(mode="solo-maintainer")
        _, output, error = self._run("--format", "json")
        self.assertFalse(error)
        finding = next(
            item for item in json.loads(output)["results"]
            if item["status"] == "REVIEW_REQUIRED"
        )
        self._write_reviews([{
            "id": "SOLO-REVIEW",
            "rule": finding["rule"],
            "ruleDigest": finding["ruleDigest"],
            "scope": finding["scope"],
            "subjectFingerprint": finding["reviewFingerprint"],
            "decision": "The sole maintainer accepts this exact semantic subject.",
            "authorityId": "test-owner",
            "reviewedBy": ["@test-owner"],
            "approvalEvidence": "github-maintainer-attestation:https://github.com/example/project/issues/1#issuecomment-1",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewedAtRevision": self.initial_revision,
            "reviewWhen": ["The subject fingerprint changes"],
        }])

        code, output, error = self._run("--format", "json", "--fail-on-review")
        self.assertEqual(0, code, error)
        self.assertTrue(any(
            item["rule"] == finding["rule"] and item["status"] == "REVIEWED"
            for item in json.loads(output)["results"]
        ))

    def test_solo_maintainer_rejects_pr_review_evidence_and_multiple_principals(self) -> None:
        self._write_authorities(mode="solo-maintainer", principals=["@test-owner", "@second-owner"])
        (self.root / ".github/CODEOWNERS").write_text("* @test-owner @second-owner\n", encoding="utf-8")
        _, output, _ = self._run("--format", "json")
        finding = next(
            item for item in json.loads(output)["results"]
            if item["status"] == "REVIEW_REQUIRED"
        )
        self._write_reviews([{
            "id": "INVALID-SOLO-REVIEW",
            "rule": finding["rule"],
            "ruleDigest": finding["ruleDigest"],
            "scope": finding["scope"],
            "subjectFingerprint": finding["reviewFingerprint"],
            "decision": "This record uses team evidence in solo mode.",
            "authorityId": "test-owner",
            "reviewedBy": ["@test-owner"],
            "approvalEvidence": "github-pr-review:not-valid-for-solo-mode",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewedAtRevision": self.initial_revision,
            "reviewWhen": ["The subject changes"],
        }])

        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("Solo-maintainer governance requires exactly one unique authority principal", output)
        self.assertIn("Solo-maintainer GitHub review requires", output)

    def test_stale_rule_digest_prevents_semantic_review_from_applying(self) -> None:
        _, output, _ = self._run("--format", "json")
        finding = next(
            item for item in json.loads(output)["results"]
            if item["status"] == "REVIEW_REQUIRED"
        )
        self._write_reviews([{
            "id": "STALE-REVIEW",
            "rule": finding["rule"],
            "ruleDigest": "sha256:" + "0" * 64,
            "scope": finding["scope"],
            "subjectFingerprint": finding["reviewFingerprint"],
            "decision": "Accepted under previous semantics.",
            "authorityId": "test-owner",
            "reviewedBy": ["@test-owner"],
            "approvalEvidence": "github-pr-review:test-approved-review",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewedAtRevision": self.initial_revision,
            "reviewWhen": ["The rule semantics change"],
        }])
        code, output, _ = self._run("--format", "json", "--fail-on-review")
        self.assertEqual(1, code)
        results = json.loads(output)["results"]
        self.assertFalse(any(item["status"] == "REVIEWED" for item in results))
        self.assertTrue(any(
            item["rule"] == "REV001"
            and item["status"] == "REVIEW_REQUIRED"
            and item["evidence"].get("staleRuleDigest")
            for item in results
        ))

    def test_base_dependent_review_is_not_stale_without_a_base(self) -> None:
        self.policy["dependencyRules"] = [{
            "from": {"ownerKind": "host"},
            "to": {"ownerKind": "module"},
            "decisionRefs": ["architecture/decisions/ADR-001-orders.md"],
        }]
        self._write_policy()
        _, output, error = self._run("--base-ref", "HEAD", "--format", "json")
        self.assertFalse(error)
        report = json.loads(output)
        reviews = []
        for index, finding in enumerate(
            result for result in report["results"]
            if result["status"] == "REVIEW_REQUIRED"
        ):
            reviews.append({
                "id": f"BASE-REVIEW-{index}",
                "rule": finding["rule"],
                "ruleDigest": finding["ruleDigest"],
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
        self.assertTrue(any(review["rule"] == "CHG001" for review in reviews))
        self._write_reviews(reviews)

        code, output, error = self._run("--base-ref", "HEAD", "--fail-on-review")
        self.assertEqual(0, code, error)
        self.assertIn("[REVIEWED] CHG001", output)

        code, output, error = self._run("--format", "json", "--fail-on-review")
        self.assertEqual(0, code, error)
        results = json.loads(output)["results"]
        self.assertTrue(any(
            item["rule"] == "CHG001" and item["status"] == "NOT_APPLICABLE"
            for item in results
        ))
        self.assertFalse(any(
            item["rule"] == "REV001" and item["status"] == "REVIEW_REQUIRED"
            for item in results
        ))

    def test_declared_authority_must_exist_in_codeowners(self) -> None:
        (self.root / ".github/CODEOWNERS").write_text("* @someone-else\n", encoding="utf-8")
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] AUT001", output)

    def test_codeowners_principal_must_cover_each_declared_scope(self) -> None:
        (self.root / ".github/CODEOWNERS").write_text("/README.md @test-owner\n", encoding="utf-8")
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] AUT001", output)
        self.assertIn("not covered by CODEOWNERS patterns", output)

    def test_codeowners_override_cannot_remove_root_authority_from_github(self) -> None:
        (self.root / ".github/CODEOWNERS").write_text(
            "* @test-owner\n/.github/ @workflow-owner\n",
            encoding="utf-8",
        )
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] AUT001", output)
        self.assertIn("narrower patterns", output)

    def test_source_import_detects_module_to_host_without_project_reference(self) -> None:
        source = self.root / "src/Modules/Orders/Features/OrderLifecycle/CreateOrder.cs"
        source.write_text(
            "using Example.Cli;\nnamespace Example.Orders.Features.OrderLifecycle;\n",
            encoding="utf-8",
        )
        code, output, _ = self._run()
        self.assertEqual(1, code)
        self.assertIn("[FAIL] DEP001 src/Modules/Orders/Features/OrderLifecycle/CreateOrder.cs", output)

    def test_unresolved_local_namespace_requires_review_instead_of_passing_dep001(self) -> None:
        self.policy["hosts"][0]["namespacePatterns"] = ["example", "example.*"]
        self._write_policy()
        source = self.root / "src/Modules/Orders/Features/OrderLifecycle/CreateOrder.cs"
        source.write_text(
            "using Example.Cli;\nnamespace Example.Orders.Features.OrderLifecycle;\n",
            encoding="utf-8",
        )

        code, output, _ = self._run()

        self.assertEqual(1, code)
        self.assertIn("[REVIEW_REQUIRED] DEP001", output)
        self.assertIn("cannot be assigned to exactly one declared owner", output)
        self.assertNotIn("[PASS] DEP001", output)

    def test_dep001_groups_repeated_resolution_consequences_by_root_cause(self) -> None:
        self.policy["hosts"][0]["namespacePatterns"] = ["example", "example.*"]
        self._write_policy()
        (self.root / "src/Hosts/Cli/Program.cs").write_text(
            "using System;\n"
            "using Example.Orders;\n"
            "using External.Package;\n"
            "namespace Example.Cli;\n",
            encoding="utf-8",
        )

        code, output, _ = self._run()

        self.assertEqual(1, code)
        self.assertEqual(1, output.count("[REVIEW_REQUIRED] DEP001 src/Hosts/Cli/Program.cs"))
        self.assertLess(
            output.index("[FAIL] ARC001 src/Hosts/Cli/Program.cs"),
            output.index("[REVIEW_REQUIRED] DEP001 src/Hosts/Cli/Program.cs"),
        )

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

    def test_reclassifying_normative_material_as_human_requires_decision_and_review(self) -> None:
        empty_policy = {
            "modules": [],
            "hosts": [],
            "projects": [],
            "allowedProjectDependencies": [],
            "dependencyRules": [],
        }
        reference = "package:data/norms/agent-core.md"
        context = SimpleNamespace(
            root=self.root,
            policy=empty_policy,
            base_policy=empty_policy,
            norms={"documents": [{
                "reference": reference,
                "enforcer": "human",
                "decisionRefs": ["package:data/norms/decisions/ADR-002-enforcement-oriented-norms.md"],
            }]},
            base_norms={"documents": [{
                "reference": reference,
                "enforcer": "agent",
                "decisionRefs": [],
            }]},
            base_revision=self.initial_revision,
        )
        findings = _rule_policy_growth(context)
        self.assertEqual(1, len(findings))
        self.assertEqual("REVIEW_REQUIRED", findings[0].status)
        self.assertEqual(reference, findings[0].scope)

        context.norms["documents"][0]["decisionRefs"] = []
        findings = _rule_policy_growth(context)
        self.assertEqual("FAIL", findings[0].status)

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
            "ruleDigest": self.rule_digests["DEP003"],
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

    def test_waiver_contract_requires_rule_digest(self) -> None:
        self.policy["allowedProjectDependencies"] = []
        self._write_policy()
        self._write_waivers([{
            "id": "LEGACY-001",
            "rule": "DEP003",
            "scope": "src/Hosts/Cli/Cli.csproj",
            "decision": "Legacy waiver.",
            "reason": "Exercise required digest binding.",
            "risk": "The semantic grant is ambiguous.",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewWhen": ["The waiver is migrated"],
        }])
        code, _, error = self._run()
        self.assertEqual(2, code)
        self.assertIn("missing required property 'ruleDigest'", error)

    def test_review_contract_requires_rule_digest(self) -> None:
        self._write_reviews([{
            "id": "LEGACY-REVIEW-001",
            "rule": "CHG001",
            "scope": ".agentic/policies/architecture/project-policy.json",
            "subjectFingerprint": "sha256:" + "0" * 64,
            "decision": "Legacy review.",
            "authorityId": "test-owner",
            "reviewedBy": ["@test-owner"],
            "approvalEvidence": "github-pr-review:https://example.invalid/review/1",
            "authorizedBy": ["architecture/decisions/ADR-001-orders.md"],
            "reviewedAtRevision": self.initial_revision,
            "reviewWhen": ["The review is migrated"],
        }])
        code, _, error = self._run()
        self.assertEqual(2, code)
        self.assertIn("missing required property 'ruleDigest'", error)

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

    def test_init_proposes_policy_from_observed_dotnet_architecture(self) -> None:
        target = self.root / "initialized"
        module = target / "src/Modules/Orders"
        host = target / "src/Hosts/Cli"
        test = target / "tests/EndToEnd/Cli"
        module.mkdir(parents=True)
        host.mkdir(parents=True)
        test.mkdir(parents=True)
        (module / "Orders.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Orders</AssemblyName></PropertyGroup></Project>\n',
            encoding="utf-8",
        )
        (host / "Cli.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>example</AssemblyName></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../../Modules/Orders/Orders.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        (test / "Example.Cli.EndToEndTests.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Example.Cli.EndToEndTests</AssemblyName></PropertyGroup>'
            '<ItemGroup><ProjectReference Include="../../../src/Hosts/Cli/Cli.csproj" /></ItemGroup></Project>\n',
            encoding="utf-8",
        )
        (module / "Order.cs").write_text("namespace Example.Orders;\n", encoding="utf-8")
        (host / "Program.cs").write_text("namespace Example.Cli;\n", encoding="utf-8")
        initialize(target, "@architecture-team")
        self.assertTrue((target / ".agentic/toolchain.json").is_file())
        self.assertTrue((target / ".agentic/policies/architecture/authorities.json").is_file())
        policy_path = target / ".agentic/policies/architecture/project-policy.json"
        self.assertTrue(policy_path.is_file())
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.assertEqual("dotnet", policy["adapter"])
        self.assertEqual(["src/Modules/Orders"], [item["root"] for item in policy["modules"]])
        self.assertEqual(["src/Hosts/Cli"], [item["root"] for item in policy["hosts"]])
        self.assertEqual(["Example.Orders", "Example.Orders.*"], policy["modules"][0]["namespacePatterns"])
        self.assertEqual(["Example.Cli", "Example.Cli.*"], policy["hosts"][0]["namespacePatterns"])
        self.assertEqual(3, len(policy["projects"]))
        test_declaration = next(item for item in policy["projects"] if item["path"].startswith("tests/"))
        self.assertEqual("test", test_declaration["role"])
        self.assertEqual({
            ("src/Hosts/Cli/Cli.csproj", "src/Modules/Orders/Orders.csproj"),
            ("tests/EndToEnd/Cli/Example.Cli.EndToEndTests.csproj", "src/Hosts/Cli/Cli.csproj"),
        }, {
            (item["from"], item["to"])
            for item in policy["allowedProjectDependencies"]
        })
        self.assertIn("* @architecture-team", (target / ".github/CODEOWNERS").read_text(encoding="utf-8"))
        self.assertFalse((target / "tools/architecture").exists())

    def test_adopted_dotnet_policy_detects_conclave_style_import_without_project_reference(self) -> None:
        target = self.root / "conclave-style"
        module = target / "src/Modules/Planning"
        feature = module / "Features/Plan"
        host = target / "src/Hosts/Cli"
        test = target / "tests/EndToEnd/Cli"
        feature.mkdir(parents=True)
        host.mkdir(parents=True)
        test.mkdir(parents=True)
        (module / "Planning.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Conclave.Planning</AssemblyName>'
            '</PropertyGroup></Project>\n',
            encoding="utf-8",
        )
        (host / "Cli.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType>'
            '<AssemblyName>conclave</AssemblyName></PropertyGroup></Project>\n',
            encoding="utf-8",
        )
        planning_source = feature / "CreatePlan.cs"
        planning_source.write_text(
            "namespace Conclave.Planning.Features.Plan;\n",
            encoding="utf-8",
        )
        (host / "Program.cs").write_text("namespace Conclave.Cli;\n", encoding="utf-8")
        (test / "Conclave.Cli.EndToEndTests.csproj").write_text(
            '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><AssemblyName>Conclave.Cli.EndToEndTests</AssemblyName>'
            '</PropertyGroup><ItemGroup><ProjectReference Include="../../../src/Hosts/Cli/Cli.csproj" />'
            '</ItemGroup></Project>\n',
            encoding="utf-8",
        )
        (test / "CliTests.cs").write_text(
            "namespace Conclave.Cli.EndToEndTests;\n",
            encoding="utf-8",
        )
        (module / "AGENTS.md").write_text("# Planning\n", encoding="utf-8")
        (module / "module.contract.yml").write_text(
            """id: planning
name: Planning
purpose: Plans current work.
intent:
  aliases:
    - planning
ownership:
  domain: planning
  authoritative_data: []
risk:
  default: medium
  reasons: []
invariants:
  - domain/planning.md#identity
architecture_decisions:
  - architecture/decisions/ADR-001-planning.md
""",
            encoding="utf-8",
        )
        (target / "domain").mkdir()
        (target / "domain/planning.md").write_text("# Planning\n\n## Identity\n", encoding="utf-8")
        (target / "architecture/decisions").mkdir(parents=True)
        (target / "architecture/decisions/ADR-001-planning.md").write_text(
            "# Planning boundary\n",
            encoding="utf-8",
        )

        initialize(target, "@architecture-team")
        policy = json.loads(
            (target / ".agentic/policies/architecture/project-policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual(["Conclave.Cli", "Conclave.Cli.*"], policy["hosts"][0]["namespacePatterns"])
        planning_source.write_text(
            "using Conclave.Cli;\nnamespace Conclave.Planning.Features.Plan;\n",
            encoding="utf-8",
        )

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = run(["--root", str(target)])

        output = stdout.getvalue() + stderr.getvalue()
        self.assertEqual(1, code, output)
        self.assertIn("[PASS] ARC001", output)
        self.assertIn("[FAIL] DEP001 src/Modules/Planning/Features/Plan/CreatePlan.cs", output)
        self.assertLess(
            output.index("[FAIL] DEP001"),
            output.index("[REVIEW_REQUIRED] FEAT001"),
        )

    def test_init_can_bootstrap_an_empty_repository_with_explicit_adapter(self) -> None:
        target = self.root / "empty-initialized"
        target.mkdir()
        initialize(target, "@architecture-team", adapter="dotnet")
        policy = json.loads(
            (target / ".agentic/policies/architecture/project-policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual([], policy["modules"])
        self.assertEqual([], policy["projects"])
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = run(["--root", str(target), "--fail-on-review"])
        self.assertEqual(0, code, stderr.getvalue() + stdout.getvalue())
        repeated = initialize(target, "@architecture-team")
        self.assertEqual("existing", repeated["policyProposal"]["basis"])
        self.assertEqual([], repeated["created"])

    def test_init_supports_solo_maintainer_governance(self) -> None:
        target = self.root / "solo-initialized"
        target.mkdir()
        initialize(
            target,
            "@solo-owner",
            adapter="dotnet",
            authority_mode="solo-maintainer",
        )
        authorities = json.loads(
            (target / ".agentic/policies/architecture/authorities.json").read_text(encoding="utf-8")
        )
        self.assertEqual("solo-maintainer", authorities["enforcement"]["mode"])
        self.assertEqual(
            ["pull-request", "no-direct-push", "required-status-checks"],
            authorities["enforcement"]["requirements"],
        )

    def _existing_python_repository(self, name: str) -> Path:
        target = self.root / name
        package = target / "src/acme_orders"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "orders.py").write_text("class Order:\n    pass\n", encoding="utf-8")
        (target / "pyproject.toml").write_text(
            '[project]\nname = "acme-orders"\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        return target

    def test_adopt_dry_run_plans_existing_repository_without_writes(self) -> None:
        target = self._existing_python_repository("adopt-dry-run")
        before = sorted(path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file())
        report, code = adopt(
            target,
            "@architecture-team",
            ci_provider="github",
            dry_run=True,
        )
        after = sorted(path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file())
        self.assertEqual(0, code)
        self.assertEqual("PLAN", report["result"])
        self.assertEqual("PLANNED", report["ci"]["status"])
        self.assertIn(".agentic/toolchain.json", report["initialization"]["planned"])
        self.assertEqual("python", report["initialization"]["projectPolicy"]["adapter"])
        self.assertTrue(report["initialization"]["projectPolicy"]["modules"])
        self.assertTrue(any(item["kind"] == "MODULE_CONTEXT" for item in report["requiredActions"]))
        self.assertEqual(before, after)
        self.assertFalse((target / ".agentic").exists())

    def test_adopt_is_dispatched_by_the_public_cli(self) -> None:
        target = self._existing_python_repository("adopt-public-cli")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = cli([
                "adopt",
                "--root", str(target),
                "--codeowner", "@architecture-team",
                "--dry-run",
            ])
        self.assertEqual(0, code, stderr.getvalue())
        self.assertEqual("PLAN", json.loads(stdout.getvalue())["result"])
        self.assertFalse((target / ".agentic").exists())
        self.assertFalse((target / ".github").exists())

    def test_adopt_applies_mechanics_reports_semantics_and_is_idempotent(self) -> None:
        target = self._existing_python_repository("adopt-apply")
        report, code = adopt(
            target,
            "@solo-owner",
            authority_mode="solo-maintainer",
            ci_provider="github",
            allow_dirty=True,
        )
        self.assertEqual(1, code)
        self.assertEqual("ACTION_REQUIRED", report["result"])
        self.assertEqual("CREATED", report["ci"]["status"])
        self.assertEqual("GENERATED", report["contextIndex"]["status"])
        self.assertIn(".agentic/toolchain.json", report["initialization"]["created"])
        self.assertTrue(any(item["kind"] == "SEMANTIC_REVIEW" for item in report["requiredActions"]))
        self.assertTrue(any(item["kind"] == "MODULE_CONTEXT" for item in report["requiredActions"]))
        workflow = (target / ".github/workflows/architecture.yml").read_text(encoding="utf-8")
        self.assertIn(f"agentic-architecture-kit=={__version__}", workflow)
        self.assertIn("actions/checkout@v7", workflow)
        self.assertIn("actions/upload-artifact@v7", workflow)
        policy_before = (target / ".agentic/policies/architecture/project-policy.json").read_text(encoding="utf-8")

        repeated, repeated_code = adopt(
            target,
            "@solo-owner",
            authority_mode="solo-maintainer",
            ci_provider="github",
            allow_dirty=True,
        )
        self.assertEqual(1, repeated_code)
        self.assertEqual([], repeated["initialization"]["created"])
        self.assertEqual("EXISTING", repeated["ci"]["status"])
        self.assertEqual(
            policy_before,
            (target / ".agentic/policies/architecture/project-policy.json").read_text(encoding="utf-8"),
        )

    def test_adopt_preserves_existing_ci_and_reports_missing_gate(self) -> None:
        target = self._existing_python_repository("adopt-existing-ci")
        workflow = target / ".github/workflows/architecture.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: Existing workflow\n", encoding="utf-8")
        report, code = adopt(
            target,
            "@architecture-team",
            ci_provider="github",
            dry_run=True,
        )
        self.assertEqual(0, code)
        self.assertEqual("REVIEW_REQUIRED", report["ci"]["status"])
        self.assertTrue(any(item["kind"] == "CI_INTEGRATION" for item in report["requiredActions"]))
        self.assertEqual("name: Existing workflow\n", workflow.read_text(encoding="utf-8"))

    def test_adopt_refuses_to_mix_with_dirty_git_work_without_authorization(self) -> None:
        target = self.root / "adopt-dirty"
        target.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)
        source = target / "app.py"
        source.write_text("value = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "app.py"], cwd=target, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "initial"],
            cwd=target,
            check=True,
        )
        source.write_text("value = 2\n", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "uncommitted changes"):
            adopt(target, "@architecture-team", adapter="python")
        self.assertFalse((target / ".agentic").exists())

    def test_adopt_rejects_an_external_report_path_before_writing(self) -> None:
        target = self._existing_python_repository("adopt-external-report")
        with self.assertRaisesRegex(ContractError, "must stay inside"):
            adopt(
                target,
                "@architecture-team",
                output=str(self.root / "outside.json"),
            )
        self.assertFalse((target / ".agentic").exists())

    def test_solo_maintainer_review_template_uses_declared_authority_and_attestation(self) -> None:
        self._write_authorities(mode="solo-maintainer")
        code, _, error = self._run("--write-review-template", "solo-reviews.json")
        self.assertEqual(0, code, error)
        template = json.loads((self.root / "solo-reviews.json").read_text(encoding="utf-8"))
        self.assertGreater(len(template["reviews"]), 0)
        for review in template["reviews"]:
            self.assertEqual("test-owner", review["authorityId"])
            self.assertEqual(["@test-owner"], review["reviewedBy"])
            self.assertTrue(review["approvalEvidence"].startswith("github-maintainer-attestation:https://github.com/"))

    def test_init_proposes_policy_from_observed_python_architecture(self) -> None:
        target = self.root / "python-initialized"
        package = target / "src/acme_orders"
        tools = target / "tools"
        package.mkdir(parents=True)
        tools.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "orders.py").write_text("from dataclasses import dataclass\n", encoding="utf-8")
        (tools / "cli.py").write_text("import acme_orders\n", encoding="utf-8")
        (target / "pyproject.toml").write_text(
            '[project]\nname = "acme-orders"\nversion = "1.0.0"\n',
            encoding="utf-8",
        )
        result = initialize(target, "@architecture-team")
        policy = json.loads(
            (target / ".agentic/policies/architecture/project-policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual("python", result["adapter"])
        self.assertEqual(["src/acme_orders"], [item["root"] for item in policy["modules"]])
        self.assertEqual(["tools/cli.py"], [item["root"] for item in policy["hosts"]])
        self.assertEqual(["pyproject.toml"], [item["path"] for item in policy["projects"]])
        self.assertFalse((target / ".agentic/contracts").exists())

    def test_every_automatic_rule_has_a_negative_mutation(self) -> None:
        mutations = {
            "POL001": "test_invalid_policy_role_is_rejected_by_pol001_gate",
            "ARC001": "test_test_role_cannot_hide_a_production_module_dependency",
            "MOD001": "test_missing_module_router_fails_mod001",
            "MOD002": "test_wrong_module_contract_identity_fails_mod002",
            "MOD003": "test_technical_module_name_fails_mod003",
            "HOST001": "test_undeclared_host_source_fails_host001",
            "DEP001": "test_adopted_dotnet_policy_detects_conclave_style_import_without_project_reference",
            "DEP002": "test_cross_module_implementation_dependency_fails_dep002",
            "DEP003": "test_unapproved_project_dependency_fails",
            "STR001": "test_forbidden_catch_all_directory_fails_str001",
            "DOC001": "test_missing_document_anchor_is_a_failure",
            "WVR001": "test_stale_rule_digest_prevents_waiver_from_silencing_a_violation",
            "AUT001": "test_codeowners_override_cannot_remove_root_authority_from_github",
            "REV001": "test_stale_rule_digest_prevents_semantic_review_from_applying",
        }
        automatic = {
            rule["id"]
            for rule in read_bundled_json("data/rules.json")["rules"]
            if rule["automatic"]
        }
        self.assertEqual(automatic, set(mutations))
        for rule, test_name in mutations.items():
            with self.subTest(rule=rule):
                self.assertTrue(callable(getattr(type(self), test_name, None)), test_name)

    def test_offline_export_is_explicit_and_contains_portable_assets(self) -> None:
        target = self.root / "offline"
        manifest = export_payload(target)
        exported = target / f"agentic-architecture-kit-{__version__}"
        self.assertTrue((exported / "agentic_architecture_kit/data/rules.json").is_file())
        self.assertTrue((exported / "agentic_architecture_kit/data/norms/agent-core.md").is_file())
        self.assertTrue((exported / "agentic_architecture_kit/data/guides/adapter-development.md").is_file())
        self.assertTrue((exported / "agentic_architecture_kit/data/guides/bootstrap.md").is_file())
        self.assertTrue((exported / "agentic_architecture_kit/data/guides/github-governance.md").is_file())
        self.assertTrue((exported / "agentic_architecture_kit/data/templates/project/AGENTS.md").is_file())
        self.assertTrue((exported / "agentic_architecture_kit/data/templates/project/github-architecture.yml").is_file())
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
