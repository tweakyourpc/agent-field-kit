#!/usr/bin/env python3
"""Smoke tests for Agent Field Kit benchmark integrity paths."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "agent-field-kit"
CODEX_ADAPTER = ROOT / "adapters" / "codex-bench-adapter.py"


def run(command: list[str], cwd: Path | None = None, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
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
        "target = repo / 'BENCHMARK.md'",
        "lines = target.read_text(encoding='utf-8', errors='replace').splitlines()",
        "kept = [line for line in lines if 'Agent Field Kit benchmark poison' not in line]",
        "target.write_text('\\n'.join(kept).rstrip() + '\\n', encoding='utf-8')",
        "subprocess.run(['git', 'add', '-A'], cwd=repo, check=True)",
        "subprocess.run(['git', 'commit', '-m', 'Fix benchmark poison'], cwd=repo, check=False)",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_delete_agent(path: Path) -> None:
    lines = [
        "from pathlib import Path",
        "import subprocess, sys",
        "repo = Path(sys.argv[1])",
        "target = repo / 'BENCHMARK.md'",
        "if target.exists():",
        "    target.unlink()",
        "subprocess.run(['git', 'add', '-A'], cwd=repo, check=True)",
        "subprocess.run(['git', 'commit', '-m', 'Delete benchmark poison'], cwd=repo, check=False)",
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


def test_delete_agent_fails(base: Path) -> None:
    repo = init_repo(base / "delete")
    agent = base / "delete_agent.py"
    write_delete_agent(agent)
    proc = run_bench(repo, agent)
    if proc.returncode == 0:
        raise AssertionError("delete benchmark unexpectedly passed\n" + proc.stdout)
    result = read_last_result(repo)
    assert result["passed"] is False, result
    assert result["resolved"] is False, result
    assert result["hooks_unchanged"] is True, result


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


def test_codex_adapter_stdin(base: Path) -> None:
    task = base / "task.md"
    captured = base / "captured.txt"
    fake_codex = base / "fake-codex.py"
    task.write_text("Benchmark task\nLine two\n", encoding="utf-8")
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "data = sys.stdin.read()\n"
        "open(os.environ['CAPTURED_TASK'], 'w', encoding='utf-8').write(data)\n"
        "sys.exit(0 if sys.argv[1:3] == ['exec', '-'] else 2)\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    env = os.environ.copy()
    env["CAPTURED_TASK"] = str(captured)
    proc = run([sys.executable, str(CODEX_ADAPTER), "--codex", str(fake_codex), str(task)], cwd=ROOT, env=env)
    if proc.returncode != 0:
        raise AssertionError(proc.stdout)
    assert captured.read_text(encoding="utf-8") == task.read_text(encoding="utf-8")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="afk-bench-smoke-"))
    try:
        test_good_agent_passes(tmp)
        test_delete_agent_fails(tmp)
        test_hook_tamper_fails(tmp)
        test_codex_adapter_stdin(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("bench smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
