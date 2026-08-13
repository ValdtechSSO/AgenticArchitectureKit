from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys

TOOL_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = TOOL_ROOT.parents[1]
sys.path.insert(0, str(TOOL_ROOT))

from validate import run  # noqa: E402
from validator.contracts import ContractError, load_yaml_subset  # noqa: E402


class ArchitectureValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        schema_source = REPOSITORY_ROOT / ".agentic/contracts/schemas"
        schema_target = self.root / ".agentic/contracts/schemas"
        schema_target.mkdir(parents=True)
        for name in (
            "architecture-policy.schema.json",
            "architecture-waivers.schema.json",
            "architecture-result.schema.json",
            "module-contract.schema.json",
        ):
            shutil.copyfile(schema_source / name, schema_target / name)

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
            "$schema": "../../contracts/schemas/architecture-policy.schema.json",
            "version": 1,
            "project": "example",
            "adapter": "dotnet",
            "roots": {"modules": "src/Modules", "hosts": "src/Hosts"},
            "projectSearchRoots": ["src"],
            "structureSearchRoots": ["src"],
            "moduleContract": {
                "fileName": "module.contract.yml",
                "schema": ".agentic/contracts/schemas/module-contract.schema.json",
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
                }
            ],
            "hosts": [
                {
                    "id": "cli",
                    "root": "src/Hosts/Cli",
                    "allowedSourcePatterns": ["Program.cs"],
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
        }
        self.policy_path = self.root / ".agentic/policies/architecture/project-policy.json"
        self.waiver_path = self.root / ".agentic/policies/architecture/waivers.json"
        self.policy_path.parent.mkdir(parents=True)
        self._write_policy()
        self._write_waivers([])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_policy(self) -> None:
        self.policy_path.write_text(json.dumps(self.policy), encoding="utf-8")

    def _write_waivers(self, waivers: list[dict]) -> None:
        self.waiver_path.write_text(
            json.dumps({"version": 1, "waivers": waivers}), encoding="utf-8"
        )

    def _run(self, *arguments: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = run(
                [
                    "--root",
                    str(self.root),
                    "--catalog",
                    str(TOOL_ROOT / "rules.json"),
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

    def test_yaml_subset_rejects_mapping_sequence_items(self) -> None:
        path = self.root / "invalid.yml"
        path.write_text("items:\n  - id: unsupported\n", encoding="utf-8")
        with self.assertRaises(ContractError):
            load_yaml_subset(path)


if __name__ == "__main__":
    unittest.main()
