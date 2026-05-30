#!/usr/bin/env python3
"""Run Codex against an Agent Field Kit benchmark task file."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="codex-bench-adapter.py",
        description="Read a benchmark task file and pass it to `codex exec` over stdin.",
    )
    parser.add_argument("task_file", help="Path to .agent-field-kit/bench-task.md")
    parser.add_argument(
        "--codex",
        default=os.environ.get("CODEX_BIN", "codex"),
        help="Codex executable path; defaults to CODEX_BIN or `codex` on PATH",
    )
    parser.add_argument(
        "codex_args",
        nargs=argparse.REMAINDER,
        help="Optional extra args for `codex exec` after `--`, for example: -- --sandbox workspace-write",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    task_file = Path(args.task_file).expanduser()
    if not task_file.exists():
        print(f"Error: task file not found: {task_file}", file=sys.stderr)
        return 1
    if not task_file.is_file():
        print(f"Error: task path is not a file: {task_file}", file=sys.stderr)
        return 1

    task_prompt = task_file.read_text(encoding="utf-8")
    extra_args = list(args.codex_args)
    if extra_args and extra_args[0] == "--":
        extra_args = extra_args[1:]
    command = [args.codex, "exec", *extra_args, "-"]
    print("[adapter] Handing benchmark task to Codex via stdin.", flush=True)
    try:
        proc = subprocess.run(command, input=task_prompt, text=True, check=False)
    except KeyboardInterrupt:
        print("\n[adapter] Interrupted during Codex execution.", file=sys.stderr)
        return 130
    except OSError as exc:
        print(f"Error: failed to spawn Codex process: {exc}", file=sys.stderr)
        return 127
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
