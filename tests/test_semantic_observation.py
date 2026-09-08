from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agentic_architecture_kit.model import ObservedArchitecture, SourceDependency, SourceLocation
from agentic_architecture_kit.contracts import validate_schema
from agentic_architecture_kit.resources import schema as bundled_schema
from agentic_architecture_kit.semantic_observers import load_semantic_observation
from agentic_architecture_kit.semantic_observers.contracts import (
    ObservationDiagnostic,
    ObservationInput,
    SemanticCoverage,
    SemanticObservation,
)
from agentic_architecture_kit.semantic_observers.fingerprint import (
    SemanticObservationError,
    file_sha256,
    manifest_fingerprint,
    repository_path,
    validate_input_manifest,
)
from agentic_architecture_kit.semantic_observers.merge import merge_observations


class FakeEntryPoint:
    def __init__(self, name: str, observer, distribution: str | None = None):
        self.name = name
        self._observer = observer
        self.dist = type("Distribution", (), {"name": distribution})() if distribution else None

    def load(self):
        return self._observer


class SemanticObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "src/Module/Feature.cs"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("namespace Product.Module;\n", encoding="utf-8")
        self.policy = {
            "adapter": "dotnet",
            "observation": {
                "semantic": {
                    "provider": "fake",
                    "mode": "required",
                    "capabilities": ["source-dependencies"],
                }
            },
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def observation(
        self,
        *,
        coverage: str = "complete",
        truncated: bool = False,
        dependencies: tuple[SourceDependency, ...] = (),
    ) -> SemanticObservation:
        inputs = (ObservationInput("src/Module/Feature.cs", file_sha256(self.source)),)
        return SemanticObservation(
            provider="fake",
            provider_version="1.0.0",
            capability="source-dependencies",
            repository_revision="unknown",
            workspace_fingerprint=manifest_fingerprint(inputs),
            subject_path=None,
            inputs=inputs,
            coverage=SemanticCoverage(
                coverage,
                ("src/Module/Feature.cs",),
                (),
                ("net10.0",),
                truncated,
            ),
            source_dependencies=dependencies,
            diagnostics=(ObservationDiagnostic("READY", "Complete fake observation."),),
        )

    def test_loader_accepts_one_typed_complete_provider(self) -> None:
        result = load_semantic_observation(
            self.root,
            self.policy,
            entry_points=(FakeEntryPoint("fake", lambda root, config: self.observation()),),
        )
        self.assertTrue(result.available)
        self.assertEqual("complete", result.coverage)
        self.assertEqual("semantic", result.resolution_used)
        self.assertFalse(result.fallback_used)

    def test_loader_reports_missing_and_ambiguous_providers_structurally(self) -> None:
        missing = load_semantic_observation(self.root, self.policy, entry_points=())
        self.assertEqual("PROVIDER_NOT_INSTALLED", missing.reason_code)
        ambiguous = load_semantic_observation(
            self.root,
            self.policy,
            entry_points=(FakeEntryPoint("fake", None), FakeEntryPoint("fake", None)),
        )
        self.assertEqual("PROVIDER_AMBIGUOUS", ambiguous.reason_code)

    def test_policy_schema_rejects_invalid_provider_mode_and_capability(self) -> None:
        schema = bundled_schema("architecture-policy.schema.json")
        base = {
            "version": 1, "project": "example", "adapter": "dotnet",
            "roots": {"modules": "src/Modules", "hosts": "src/Hosts"},
            "projectSearchRoots": ["src"], "structureSearchRoots": ["src"],
            "moduleContract": {"fileName": "module.contract.yml", "schema": "package:module-contract.schema.json", "forbiddenStructuralFields": []},
            "technicalModuleNames": [], "forbiddenDirectoryNames": [], "modules": [],
            "hosts": [], "projects": [], "allowedProjectDependencies": [],
        }
        for semantic in (
            {"provider": "Not-Valid", "mode": "required", "capabilities": ["source-dependencies"]},
            {"provider": "fake", "mode": "auto", "capabilities": ["source-dependencies"]},
            {"provider": "fake", "mode": "required", "capabilities": ["symbols"]},
        ):
            with self.subTest(semantic=semantic):
                self.assertTrue(validate_schema({**base, "observation": {"semantic": semantic}}, schema))

    def test_loader_rejects_an_unpinned_provider_distribution(self) -> None:
        result = load_semantic_observation(
            self.root,
            self.policy,
            toolchain={"extensions": []},
            entry_points=(FakeEntryPoint("fake", lambda root, config: self.observation(), "aak-fake"),),
        )
        self.assertTrue(result.invalid)
        self.assertEqual("PROVIDER_NOT_PINNED", result.reason_code)

    def test_loader_rejects_wrong_return_type_and_capability(self) -> None:
        invalid = load_semantic_observation(
            self.root,
            self.policy,
            entry_points=(FakeEntryPoint("fake", lambda root, config: object()),),
        )
        self.assertTrue(invalid.invalid)
        self.assertEqual("INVALID_PROVIDER_OUTPUT", invalid.reason_code)
        wrong = self.observation()
        object.__setattr__(wrong, "capability", "symbols")
        capability = load_semantic_observation(
            self.root,
            self.policy,
            entry_points=(FakeEntryPoint("fake", lambda root, config: wrong),),
        )
        self.assertEqual("CAPABILITY_NOT_PROVIDED", capability.reason_code)

    def test_fingerprint_is_sorted_content_bound_and_rejects_escape(self) -> None:
        second = self.root / "src/Module/Other.cs"
        second.write_text("namespace Product.Module;\n", encoding="utf-8")
        inputs = (
            ObservationInput("src/Module/Feature.cs", file_sha256(self.source)),
            ObservationInput("src/Module/Other.cs", file_sha256(second)),
        )
        expected = manifest_fingerprint(inputs)
        self.assertEqual(expected, manifest_fingerprint(tuple(reversed(inputs))))
        self.assertEqual(expected, validate_input_manifest(self.root, inputs))
        self.source.write_text("namespace Product.Changed;\n", encoding="utf-8")
        with self.assertRaisesRegex(SemanticObservationError, "input changed"):
            validate_input_manifest(self.root, inputs)
        with self.assertRaises(SemanticObservationError):
            repository_path(self.root, "../outside.cs")
        with self.assertRaises(SemanticObservationError):
            repository_path(self.root, str(self.source))
        outside = Path(self.temporary.name).parent / "aak-semantic-outside.txt"
        outside.write_text("outside", encoding="utf-8")
        link = self.root / "src/escape.txt"
        try:
            link.symlink_to(outside)
            with self.assertRaises(SemanticObservationError):
                repository_path(self.root, "src/escape.txt")
        finally:
            outside.unlink(missing_ok=True)

    def test_loader_rejects_absolute_paths_in_persisted_diagnostics(self) -> None:
        observation = self.observation()
        object.__setattr__(
            observation,
            "diagnostics",
            (ObservationDiagnostic("LOAD", f"Loaded from {self.root}/private.sln"),),
        )
        result = load_semantic_observation(
            self.root,
            self.policy,
            entry_points=(FakeEntryPoint("fake", lambda root, config: observation),),
        )
        self.assertTrue(result.invalid)
        self.assertEqual("INVALID_PROVIDER_OUTPUT", result.reason_code)

    def test_loader_rejects_stale_hash_and_truncation_degrades_coverage(self) -> None:
        stale = self.observation()
        self.source.write_text("// dirty\n", encoding="utf-8")
        result = load_semantic_observation(
            self.root,
            self.policy,
            entry_points=(FakeEntryPoint("fake", lambda root, config: stale),),
        )
        self.assertTrue(result.invalid)
        self.assertEqual("INPUT_HASH_MISMATCH", result.reason_code)
        self.source.write_text("namespace Product.Module;\n", encoding="utf-8")
        truncated = load_semantic_observation(
            self.root,
            self.policy,
            entry_points=(FakeEntryPoint("fake", lambda root, config: self.observation(truncated=True)),),
        )
        self.assertEqual("partial", truncated.coverage)
        self.assertEqual("TRUNCATED_RESULT", truncated.reason_code)
        self.assertTrue(truncated.fallback_used)


class SemanticMergeTests(unittest.TestCase):
    def structural(self) -> ObservedArchitecture:
        return ObservedArchitecture(
            ("src/Modules/Orders",),
            ("src/Hosts/Cli",),
            (),
            ("src/Modules/Orders/Order.cs",),
            (
                SourceDependency(
                    "src/Modules/Orders/Order.cs",
                    "Example.Orders",
                    "Example.Cli",
                    "using-directive",
                    resolution="syntactic",
                    provider="dotnet-adapter",
                ),
            ),
        )

    def semantic(self, status: str, dependencies: tuple[SourceDependency, ...]) -> SemanticObservation:
        return SemanticObservation(
            "fake", "1.0.0", "source-dependencies", "revision", "sha256:" + "0" * 64, None,
            (), SemanticCoverage(status, ("src/Modules/Orders/Order.cs",), (), ("net10.0",)), dependencies,
        )

    def test_complete_coverage_removes_unused_using_and_adds_fully_qualified_edge(self) -> None:
        merged = merge_observations(self.structural(), self.semantic("complete", ()), "required")
        self.assertEqual((), merged.source_dependencies)
        semantic_edge = SourceDependency(
            "src/Modules/Orders/Order.cs", "Example.Orders", "Example.Cli", "symbol-reference",
            resolution="semantic", provider="fake", source_symbol="Example.Orders.Order",
            target_symbol="Example.Cli.ConsoleWriter", target_project_path="src/Hosts/Cli/Cli.csproj",
            locations=(SourceLocation("src/Modules/Orders/Order.cs", 3, 5, 3, 20),),
            configurations=("net10.0",),
        )
        merged = merge_observations(self.structural(), self.semantic("complete", (semantic_edge,)), "required")
        self.assertEqual((semantic_edge,), merged.source_dependencies)

    def test_partial_and_uncovered_files_preserve_syntactic_fallback(self) -> None:
        partial = merge_observations(self.structural(), self.semantic("partial", ()), "required")
        self.assertEqual(1, len(partial.source_dependencies))
        uncovered_observation = self.semantic("complete", ())
        object.__setattr__(
            uncovered_observation,
            "coverage",
            SemanticCoverage("complete", ("src/Other.cs",), (), ("net10.0",)),
        )
        uncovered = merge_observations(self.structural(), uncovered_observation, "advisory")
        self.assertEqual(1, len(uncovered.source_dependencies))

    def test_semantic_identity_keeps_same_text_with_distinct_symbols_and_configurations(self) -> None:
        first = SourceDependency(
            "src/Modules/Orders/Order.cs", "Example.Orders", "Example.Target", "symbol-reference",
            resolution="semantic", provider="fake", target_symbol="Example.Target.A", configurations=("net8.0",),
        )
        second = SourceDependency(
            "src/Modules/Orders/Order.cs", "Example.Orders", "Example.Target", "symbol-reference",
            resolution="semantic", provider="fake", target_symbol="Example.Target.B", configurations=("net10.0",),
        )
        merged = merge_observations(self.structural(), self.semantic("complete", (first, second, first)), "required")
        self.assertEqual(2, len(merged.source_dependencies))


if __name__ == "__main__":
    unittest.main()
