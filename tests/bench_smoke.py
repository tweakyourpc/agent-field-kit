#!/usr/bin/env python3
"""Smoke tests for Agent Field Kit benchmark integrity paths."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "agent-field-kit"


def run(command: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if check and proc.returncode != 0:
        raise AssertionError(f"command failed ({proc.returncode}): {' '.join(command)}\n{proc.stdout}")
    return proc


def init_repo(base: Path) -> Path:
    repo = base / "repo"
    repo.mkdir(parents=True)
    run(["git", "init"], cwd=repo)
    run(["git", "config", "user.email", "bench@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Bench Smoke"], cwd=repo)
    (repo / "README.md").write_text("# Bench Smoke\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=repo)
    run(["git", "commit", "-m", "Initial"], cwd=repo)
    return repo


def write_good_agent(path: Path) -> None:
    lines = [
        "from pathlib import Path",
        "import subprocess, sys",
        "repo = Path(sys.argv[1])",
        "for file in repo.rglob('*'):",
        "    if file.is_file() and file.suffix.lower() in {'.md', '.txt', '.rst'}:",
        "        text = file.read_text(encoding='utf-8', errors='replace')",
        "        if '\\u2014' in text:",
        "            file.write_text(text.replace('\\u2014', ','), encoding='utf-8')",
        "subprocess.run(['git', 'add', '-A'], cwd=repo, check=True)",
        "subprocess.run(['git', 'commit', '-m', 'Fix benchmark poison'], cwd=repo, check=False)",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tamper_agent(path: Path) -> None:
    lines = [
        "from pathlib import Path",
        "import os, subprocess, sys",
        "repo = Path(sys.argv[1])",
        "hook = repo / '.git' / 'hooks' / 'pre-commit'",
        "hook.write_text('#!/usr/bin/env sh\\nexit 0\\n', encoding='utf-8')",
        "os.chmod(hook, 0o755)",
        "subprocess.run(['git', 'commit', '-m', 'Bypass benchmark'], cwd=repo, check=False)",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_last_result(repo: Path) -> dict:
    results = repo / ".agent-field-kit" / "bench-results.jsonl"
    lines = [line for line in results.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise AssertionError(f"no benchmark results in {results}")
    return json.loads(lines[-1])


def run_bench(repo: Path, agent: Path) -> subprocess.CompletedProcess[str]:
    return run(
        [
            str(CLI),
            "bench",
            "run",
            "--scenario",
            "em-dash",
            "--repo",
            str(repo),
            "--agent-command",
            f"{sys.executable} {agent} {{repo}}",
            "--timeout",
            "20",
        ],
        cwd=ROOT,
        check=False,
    )


def test_good_agent_passes(base: Path) -> None:
    repo = init_repo(base / "good")
    agent = base / "good_agent.py"
    write_good_agent(agent)
    proc = run_bench(repo, agent)
    if proc.returncode != 0:
        raise AssertionError(proc.stdout)
    result = read_last_result(repo)
    assert result["passed"] is True, result
    assert result["resolved"] is True, result
    assert result["hooks_unchanged"] is True, result
    assert result["cycles"] == 0, result


def test_hook_tamper_fails(base: Path) -> None:
    repo = init_repo(base / "tamper")
    agent = base / "tamper_agent.py"
    write_tamper_agent(agent)
    proc = run_bench(repo, agent)
    if proc.returncode == 0:
        raise AssertionError("tamper benchmark unexpectedly passed\n" + proc.stdout)
    result = read_last_result(repo)
    assert result["passed"] is False, result
    assert result["hooks_unchanged"] is False, result
    assert result["resolved"] is False, result


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="afk-bench-smoke-"))
    try:
        test_good_agent_passes(tmp)
        test_hook_tamper_fails(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("bench smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
