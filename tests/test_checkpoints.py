from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from agentic_architecture_kit.checkpoint_cli import run  # noqa: E402
from agentic_architecture_kit.resources import read_text as read_bundled_text  # noqa: E402


class ExecutionCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "docs").mkdir()
        (self.root / "docs/plan.md").write_text("# Original plan\n\nBuild the durable outcome.\n", encoding="utf-8")
        (self.root / "work.txt").write_text("baseline\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Checkpoint Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "baseline"],
            cwd=self.root,
            check=True,
        )
        self.task_id = "long-task"
        self.state_path = f".agentic/runtime/checkpoints/{self.task_id}/draft-state.json"
        self._write_state()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _state(self) -> dict:
        return {
            "version": 1,
            "globalObjective": "Deliver the complete durable outcome.",
            "activeInvariants": [{
                "id": "INV-001",
                "statement": "Existing behavior remains compatible.",
                "status": "holds",
                "evidence": ["docs/plan.md"],
            }],
            "decisions": [],
            "planDeviations": [],
            "openRisks": [],
            "resolvedRisks": [],
            "nextObjective": "Implement the next bounded segment.",
        }

    def _write_state(self, state: dict | None = None) -> None:
        path = self.root / self.state_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state or self._state()), encoding="utf-8")

    def _run(self, *arguments: str) -> tuple[int, str, str]:
        output = io.StringIO()
        error = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = run([*arguments, "--root", str(self.root)] if arguments[0] != "run-test" else [
                "run-test", "--root", str(self.root), *arguments[1:]
            ])
        return code, output.getvalue(), error.getvalue()

    def _create(self, reason: str = "No tests were appropriate for this documentation checkpoint.") -> tuple[int, str, str]:
        return self._run(
            "create",
            "--task-id", self.task_id,
            "--plan", "docs/plan.md",
            "--state", self.state_path,
            "--no-tests-reason", reason,
        )

    def _resume(self) -> tuple[int, str, str]:
        return self._run("resume", "--task-id", self.task_id, "--plan", "docs/plan.md")

    def test_checkpoint_requires_resume_and_resume_rehydrates_plan_and_state(self) -> None:
        code, output, error = self._create()
        self.assertEqual(0, code, error)
        self.assertIn("Checkpoint 1 created", output)

        code, output, error = self._run("verify", "--task-id", self.task_id, "--plan", "docs/plan.md")
        self.assertEqual(1, code, error)
        self.assertIn("[REVIEW_REQUIRED] CPK004", output)

        code, output, error = self._resume()
        self.assertEqual(0, code, error)
        self.assertIn("# Original plan", output)
        self.assertIn("Build the durable outcome.", output)
        self.assertIn("# Latest durable checkpoint", output)
        self.assertIn("Deliver the complete durable outcome.", output)

        code, output, error = self._run("verify", "--task-id", self.task_id, "--plan", "docs/plan.md")
        self.assertEqual(0, code, error)
        self.assertIn("[PASS] CPK004", output)

    def test_second_checkpoint_is_rejected_until_previous_is_resumed(self) -> None:
        self.assertEqual(0, self._create()[0])
        code, _, error = self._create()
        self.assertEqual(2, code)
        self.assertIn("Resume the previous checkpoint", error)

    def test_run_test_evidence_is_generated_and_embedded_as_current(self) -> None:
        code, output, error = self._run(
            "run-test", "--task-id", self.task_id, "--", sys.executable, "-c",
            "import sys; print('out'); print('err', file=sys.stderr)"
        )
        self.assertEqual(0, code, error)
        self.assertIn("Outcome: passed", output)
        code, _, error = self._create()
        self.assertEqual(0, code, error)
        checkpoint_path = next((self.root / ".agentic/runtime/checkpoints/long-task").glob("checkpoint-*.json"))
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        self.assertEqual("passed", checkpoint["testAssessment"]["status"])
        self.assertEqual(1, len(checkpoint["testEvidence"]))
        evidence = checkpoint["testEvidence"][0]
        self.assertEqual(
            [sys.executable, "-c", "import sys; print('out'); print('err', file=sys.stderr)"],
            evidence["command"],
        )
        for stream in ("stdout", "stderr"):
            artifact = self.root / evidence[stream]["path"]
            self.assertTrue(artifact.is_file())
            self.assertEqual(evidence[stream]["bytes"], artifact.stat().st_size)
            self.assertEqual(
                evidence[stream]["digest"],
                "sha256:" + hashlib.sha256(artifact.read_bytes()).hexdigest(),
            )

    def test_checkpoint_without_test_receipt_requires_explicit_reason(self) -> None:
        code, _, error = self._run(
            "create", "--task-id", self.task_id, "--plan", "docs/plan.md", "--state", self.state_path
        )
        self.assertEqual(2, code)
        self.assertIn("--no-tests-reason", error)

    def test_unfilled_checkpoint_template_is_rejected(self) -> None:
        (self.root / self.state_path).write_text(
            read_bundled_text("data/templates/project/checkpoint-state.json"), encoding="utf-8"
        )
        code, _, error = self._create()
        self.assertEqual(2, code)
        self.assertIn("unresolved placeholder", error)

    def test_plan_change_invalidates_resume_and_verification(self) -> None:
        self.assertEqual(0, self._create()[0])
        (self.root / "docs/plan.md").write_text("# Rewritten plan\n", encoding="utf-8")
        code, _, error = self._resume()
        self.assertEqual(2, code)
        self.assertIn("does not match", error)
        code, output, error = self._run("verify", "--task-id", self.task_id, "--plan", "docs/plan.md")
        self.assertEqual(1, code, error)
        self.assertIn("[FAIL] CPK003", output)

    def test_workspace_drift_before_resume_fails_closed(self) -> None:
        self.assertEqual(0, self._create()[0])
        (self.root / "work.txt").write_text("changed without resume\n", encoding="utf-8")
        code, _, error = self._resume()
        self.assertEqual(2, code)
        self.assertIn("Workspace changed", error)
        code, output, error = self._run("verify", "--task-id", self.task_id, "--plan", "docs/plan.md")
        self.assertEqual(1, code, error)
        self.assertIn("Workspace drift occurred", output)

    def test_workspace_progress_after_resume_is_valid(self) -> None:
        self.assertEqual(0, self._create()[0])
        self.assertEqual(0, self._resume()[0])
        (self.root / "work.txt").write_text("continued after resume\n", encoding="utf-8")
        code, output, error = self._run("verify", "--task-id", self.task_id, "--plan", "docs/plan.md")
        self.assertEqual(0, code, error)
        self.assertIn("Checkpoint verification: IN_PROGRESS", output)

    def test_test_execution_after_checkpoint_requires_resume(self) -> None:
        self.assertEqual(0, self._create()[0])
        code, _, error = self._run(
            "run-test", "--task-id", self.task_id, "--", sys.executable, "-c", "pass"
        )
        self.assertEqual(2, code)
        self.assertIn("Resume the latest checkpoint", error)

    def test_failed_test_is_retained_without_becoming_green(self) -> None:
        code, output, error = self._run(
            "run-test", "--task-id", self.task_id, "--", sys.executable, "-c", "raise SystemExit(7)"
        )
        self.assertEqual(7, code, error)
        self.assertIn("Outcome: failed", output)
        code, _, error = self._create()
        self.assertEqual(0, code, error)
        checkpoint_path = next((self.root / ".agentic/runtime/checkpoints/long-task").glob("checkpoint-*.json"))
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        self.assertEqual("failed", checkpoint["testAssessment"]["status"])

    def test_open_risk_cannot_disappear_without_resolution(self) -> None:
        first = self._state()
        first["openRisks"] = [{
            "id": "RISK-001", "description": "Unverified migration.", "severity": "high",
            "mitigation": "Run migration tests.", "owner": "implementation agent", "trigger": "Before completion",
        }]
        self._write_state(first)
        self.assertEqual(0, self._create()[0])
        self.assertEqual(0, self._resume()[0])
        self._write_state(self._state())
        code, _, error = self._create()
        self.assertEqual(2, code)
        self.assertIn("Open risk disappeared", error)

    def test_cumulative_decisions_deviations_and_risk_resolution_are_enforced(self) -> None:
        first = self._state()
        first["decisions"] = [{
            "id": "DEC-001", "decision": "Keep one module.", "rationale": "No boundary is justified.",
            "status": "active", "supersededBy": "", "affectsInvariants": [],
        }]
        first["planDeviations"] = [{
            "id": "DEV-001", "planReference": "Section 2", "description": "Changed ordering.",
            "rationale": "Dependency discovered.", "impact": "No scope change.",
        }]
        first["openRisks"] = [{
            "id": "RISK-001", "description": "Coverage may be incomplete.", "severity": "medium",
            "mitigation": "Run the full suite.", "owner": "implementation agent", "trigger": "Before completion",
        }]
        self._write_state(first)
        self.assertEqual(0, self._create()[0])
        self.assertEqual(0, self._resume()[0])

        second = self._state()
        second["resolvedRisks"] = [{"riskId": "RISK-001", "resolution": "Full suite passed.", "evidence": ["test receipt"]}]
        self._write_state(second)
        code, _, error = self._create()
        self.assertEqual(2, code)
        self.assertIn("Cumulative decision disappeared", error)

        second["decisions"] = first["decisions"]
        second["planDeviations"] = first["planDeviations"]
        self._write_state(second)
        code, _, error = self._create()
        self.assertEqual(0, code, error)

    def test_invariant_removal_requires_a_new_explanatory_decision(self) -> None:
        self.assertEqual(0, self._create()[0])
        self.assertEqual(0, self._resume()[0])
        state = self._state()
        state["activeInvariants"] = [{
            "id": "INV-002", "statement": "Replacement invariant.", "status": "holds", "evidence": ["docs/plan.md"]
        }]
        self._write_state(state)
        code, _, error = self._create()
        self.assertEqual(2, code)
        self.assertIn("without a new decision", error)

        state["decisions"] = [{
            "id": "DEC-INV-001", "decision": "Replace INV-001 with INV-002.",
            "rationale": "The plan now expresses the guarantee more precisely.", "status": "active",
            "supersededBy": "", "affectsInvariants": ["INV-001"],
        }]
        self._write_state(state)
        code, _, error = self._create()
        self.assertEqual(0, code, error)

    def test_decision_rationale_cannot_be_rewritten(self) -> None:
        first = self._state()
        first["decisions"] = [{
            "id": "DEC-001", "decision": "Keep the existing boundary.",
            "rationale": "Current ownership remains cohesive.", "status": "active",
            "supersededBy": "", "affectsInvariants": [],
        }]
        self._write_state(first)
        self.assertEqual(0, self._create()[0])
        self.assertEqual(0, self._resume()[0])
        second = self._state()
        second["decisions"] = [{**first["decisions"][0], "rationale": "Rewritten history."}]
        self._write_state(second)
        code, _, error = self._create()
        self.assertEqual(2, code)
        self.assertIn("rewritten instead of superseded", error)

    def test_plan_deviation_cannot_disappear(self) -> None:
        first = self._state()
        first["planDeviations"] = [{
            "id": "DEV-001", "planReference": "Step 3", "description": "Reordered implementation.",
            "rationale": "A dependency had to land first.", "impact": "Scope stayed unchanged.",
        }]
        self._write_state(first)
        self.assertEqual(0, self._create()[0])
        self.assertEqual(0, self._resume()[0])
        self._write_state(self._state())
        code, _, error = self._create()
        self.assertEqual(2, code)
        self.assertIn("Cumulative planDeviations", error)

    def test_tampered_checkpoint_digest_fails_closed(self) -> None:
        self.assertEqual(0, self._create()[0])
        checkpoint_path = next((self.root / ".agentic/runtime/checkpoints/long-task").glob("checkpoint-*.json"))
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        checkpoint["state"]["nextObjective"] = "Tampered objective"
        checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
        code, _, error = self._run("verify", "--task-id", self.task_id, "--plan", "docs/plan.md")
        self.assertEqual(2, code)
        self.assertIn("digest does not match", error)

    def test_tampered_test_output_artifact_fails_closed(self) -> None:
        self.assertEqual(0, self._run(
            "run-test", "--task-id", self.task_id, "--", sys.executable, "-c", "print('evidence')"
        )[0])
        self.assertEqual(0, self._create()[0])
        checkpoint_path = next((self.root / ".agentic/runtime/checkpoints/long-task").glob("checkpoint-*.json"))
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        output_path = self.root / checkpoint["testEvidence"][0]["stdout"]["path"]
        output_path.write_text("tampered\n", encoding="utf-8")
        code, _, error = self._run("verify", "--task-id", self.task_id, "--plan", "docs/plan.md")
        self.assertEqual(2, code)
        self.assertIn("artifact does not match", error)


if __name__ == "__main__":
    unittest.main()
