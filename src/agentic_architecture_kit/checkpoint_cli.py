from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .checkpoints import (
    checkpoint_status,
    create_checkpoint,
    create_resume_receipt,
    record_test_execution,
    verify_checkpoint,
)
from .contracts import ContractError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aak checkpoint",
        description="Persist and verify durable state for long-running agent execution.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create", help="Create the next immutable checkpoint.")
    create.add_argument("--root", default=".", help="Repository root (default: current directory).")
    create.add_argument("--task-id", required=True)
    create.add_argument("--plan", required=True, help="Repository-relative path to the unchanged original plan.")
    create.add_argument("--state", required=True, help="Repository-relative checkpoint state JSON file.")
    create.add_argument("--no-tests-reason", help="Explicit reason when this segment produced no test evidence.")
    create.add_argument("--format", choices=("text", "json"), default="text")

    resume = commands.add_parser("resume", help="Rehydrate the original plan and latest checkpoint and write a receipt.")
    resume.add_argument("--root", default=".")
    resume.add_argument("--task-id", required=True)
    resume.add_argument("--plan", required=True)
    resume.add_argument("--format", choices=("text", "json"), default="text")

    run_test = commands.add_parser("run-test", help="Run a test command and retain content-bound execution evidence.")
    run_test.add_argument("--root", default=".")
    run_test.add_argument("--task-id", required=True)
    run_test.add_argument("test_command", nargs=argparse.REMAINDER)

    status = commands.add_parser("status", help="Report checkpoint, plan, workspace, test, risk, and resume state.")
    status.add_argument("--root", default=".")
    status.add_argument("--task-id", required=True)
    status.add_argument("--plan", required=True)

    verify = commands.add_parser("verify", help="Fail closed on an invalid, stale, or unresumed checkpoint chain.")
    verify.add_argument("--root", default=".")
    verify.add_argument("--task-id", required=True)
    verify.add_argument("--plan", required=True)
    verify.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def run(arguments: list[str] | None = None) -> int:
    args = _parser().parse_args(arguments)
    root = Path(args.root).resolve()
    try:
        if args.command == "create":
            path, checkpoint = create_checkpoint(
                root, args.task_id, args.plan, args.state, args.no_tests_reason
            )
            result = {
                "path": path.relative_to(root).as_posix(),
                "checkpointDigest": checkpoint["checkpointDigest"],
                "sequence": checkpoint["sequence"],
                "testAssessment": checkpoint["testAssessment"],
                "nextObjective": checkpoint["state"]["nextObjective"],
            }
            if args.format == "json":
                print(_json(result), end="")
            else:
                print(f"Checkpoint {result['sequence']} created: {result['path']}")
                print(f"Digest: {result['checkpointDigest']}")
                print(f"Tests: {result['testAssessment']['status']} - {result['testAssessment']['reason']}")
                print(f"Next objective: {result['nextObjective']}")
            return 0

        if args.command == "resume":
            path, receipt, checkpoint, plan_content = create_resume_receipt(
                root, args.task_id, args.plan
            )
            if args.format == "json":
                print(_json({
                    "originalPlan": {
                        "path": checkpoint["plan"]["path"],
                        "digest": checkpoint["plan"]["digest"],
                        "content": plan_content,
                    },
                    "checkpoint": checkpoint,
                    "resumeReceipt": receipt,
                    "receiptPath": path.relative_to(root).as_posix(),
                }), end="")
            else:
                print("# Original plan")
                print(f"Path: {checkpoint['plan']['path']}")
                print(f"Digest: {checkpoint['plan']['digest']}")
                print()
                print(plan_content, end="" if plan_content.endswith("\n") else "\n")
                print("\n# Latest durable checkpoint")
                print(_json(checkpoint), end="")
                print("# Resume receipt")
                print(_json({**receipt, "path": path.relative_to(root).as_posix()}), end="")
            return 0

        if args.command == "run-test":
            path, evidence, exit_code = record_test_execution(
                root, args.task_id, args.test_command
            )
            print(f"Checkpoint test evidence: {path.relative_to(root).as_posix()}")
            print(f"Evidence digest: {evidence['evidenceDigest']}")
            print(f"Outcome: {evidence['outcome']} (exit {exit_code})")
            return exit_code

        if args.command == "status":
            print(_json(checkpoint_status(root, args.task_id, args.plan)), end="")
            return 0

        if args.command == "verify":
            exit_code, findings, status = verify_checkpoint(root, args.task_id, args.plan)
            if args.format == "json":
                print(_json({"findings": findings, "checkpoint": status}), end="")
            else:
                for finding in findings:
                    print(f"[{finding['status']}] {finding['rule']} - {finding['message']}")
                print(f"Checkpoint verification: {status['status']}")
            return exit_code
    except (ContractError, OSError) as error:
        print(f"Checkpoint contract error: {error}", file=sys.stderr)
        return 2
    return 2
