#!/usr/bin/env python3
"""Shared eval harness for stack-code skill scenarios.

Each scenario script creates a throwaway, jj-colocated git repo with a bare
"upstream" remote so `jj git push` succeeds without GitHub. `gh` is shimmed via
PATH so PR create/edit/view calls are observable and `pr view --json state`
returns whatever the scenario sets in `<tmpdir>/gh-state.json`.

Stdlib only. No pytest. Each scenario is independently runnable:

    python3 evals/<scenario>.py

Exit code 0 = pass. Non-zero = fail. Each scenario tears down its tempdir.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
EXECUTE_STACK = SCRIPTS_DIR / "execute-stack.py"


@dataclass
class Repo:
    """A live jj-colocated repo wired to a bare upstream and a shimmed `gh`."""

    root: Path
    upstream: Path
    shim_dir: Path
    state_file: Path  # gh-state.json — controls what fake `gh pr view` returns
    env: dict[str, str]


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a command and optionally raise on non-zero exit."""
    res = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        capture_output=capture,
        text=True,
        check=False,
    )
    if check and res.returncode != 0:
        sys.stderr.write(
            f"\ncommand failed: {' '.join(cmd)}\n"
            f"  cwd={cwd}\n  rc={res.returncode}\n"
            f"  stdout={res.stdout}\n  stderr={res.stderr}\n"
        )
        raise SystemExit(1)
    return res


def jj(repo: Repo, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return _run(["jj", *args], cwd=repo.root, env=repo.env, check=check)


def git(repo: Repo, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return _run(["git", *args], cwd=repo.root, env=repo.env, check=check)


def write_gh_state(repo: Repo, state: str) -> None:
    """Set what the fake `gh pr view --json state` returns (e.g. 'OPEN', 'MERGED')."""
    repo.state_file.write_text(state.strip().upper() + "\n", encoding="utf-8")


def _install_gh_shim(shim_dir: Path, state_file: Path) -> Path:
    """Write a fake `gh` to `shim_dir` that emulates the subset stack-code uses.

    Behaviour:
      * `gh pr create ...`               -> prints a fake URL on stdout, exit 0.
      * `gh pr edit ...`                 -> exit 0, no output.
      * `gh pr reopen ...`               -> exit 0.
      * `gh pr view <bm> --json state -q .state` -> echoes contents of state-file.
      * `gh pr view <bm> --json baseRefName,state -q .` -> echoes JSON with state.
      * anything else                    -> exit 0, no output (defensive).
    """
    shim_dir.mkdir(parents=True, exist_ok=True)
    gh_path = shim_dir / "gh"
    bases_file = state_file.parent / "gh-bases.json"
    script = f"""#!/usr/bin/env python3
import json, sys
from pathlib import Path

STATE_FILE = Path({str(state_file)!r})
BASES_FILE = Path({str(bases_file)!r})

def read_state() -> str:
    try:
        return STATE_FILE.read_text(encoding="utf-8").strip().upper() or "OPEN"
    except FileNotFoundError:
        return "OPEN"

def load_bases() -> dict:
    try:
        return json.loads(BASES_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {{}}

def save_bases(bases: dict) -> None:
    BASES_FILE.write_text(json.dumps(bases), encoding="utf-8")

def lookup_base(bookmark: str) -> str:
    return load_bases().get(bookmark, "main")

argv = sys.argv[1:]
if len(argv) >= 2 and argv[0] == "pr" and argv[1] == "create":
    # `gh pr create --base <base> --head <bookmark> ...`
    base = head = ""
    for i, tok in enumerate(argv):
        if tok == "--base" and i + 1 < len(argv):
            base = argv[i + 1]
        if tok == "--head" and i + 1 < len(argv):
            head = argv[i + 1]
    if head:
        b = load_bases(); b[head] = base or "main"; save_bases(b)
    print("https://example.invalid/pr/" + (head or "x"))
    sys.exit(0)
if len(argv) >= 2 and argv[0] == "pr" and argv[1] == "edit":
    # `gh pr edit <bookmark> --base <base>`
    bookmark = argv[2] if len(argv) > 2 else ""
    base = ""
    for i, tok in enumerate(argv):
        if tok == "--base" and i + 1 < len(argv):
            base = argv[i + 1]
    if bookmark and base:
        b = load_bases(); b[bookmark] = base; save_bases(b)
    sys.exit(0)
if len(argv) >= 2 and argv[0] == "pr" and argv[1] == "reopen":
    sys.exit(0)
if len(argv) >= 4 and argv[0] == "pr" and argv[1] == "view":
    bookmark = argv[2] if len(argv) > 2 else ""
    json_idx = argv.index("--json") if "--json" in argv else -1
    fields = argv[json_idx + 1] if json_idx != -1 else ""
    state = read_state()
    base = lookup_base(bookmark)
    if fields == "state":
        # The real `gh -q .state` extracts the field; we emit it bare.
        print(state)
        sys.exit(0)
    if "baseRefName" in fields:
        print(json.dumps({{"baseRefName": base, "state": state}}))
        sys.exit(0)
    print(json.dumps({{"state": state}}))
    sys.exit(0)
# Defensive default — never block.
sys.exit(0)
"""
    gh_path.write_text(script, encoding="utf-8")
    gh_path.chmod(0o755)
    return gh_path


@contextlib.contextmanager
def fresh_repo(*, prefix: str = "stack-code-eval-") -> Iterator[Repo]:
    """Build a colocated jj repo with a bare upstream + shimmed gh; clean up after."""
    tmp = Path(tempfile.mkdtemp(prefix=prefix))
    try:
        upstream = tmp / "upstream.git"
        root = tmp / "work"
        shim_dir = tmp / "shims"
        state_file = tmp / "gh-state.json"
        upstream.mkdir(parents=True)
        root.mkdir(parents=True)
        # Default state for `gh pr view --json state` until a scenario flips it.
        state_file.write_text("OPEN\n", encoding="utf-8")

        gh_shim = _install_gh_shim(shim_dir, state_file)

        # Build env: shim FIRST on PATH, set jj/git identity so commits succeed.
        env = os.environ.copy()
        env["PATH"] = f"{shim_dir}{os.pathsep}{env.get('PATH', '')}"
        env["STACK_CODE_AUTO_APPROVE"] = "1"
        env["JJ_USER"] = "Eval"
        env["JJ_EMAIL"] = "eval@example.invalid"
        env["GIT_AUTHOR_NAME"] = "Eval"
        env["GIT_AUTHOR_EMAIL"] = "eval@example.invalid"
        env["GIT_COMMITTER_NAME"] = "Eval"
        env["GIT_COMMITTER_EMAIL"] = "eval@example.invalid"

        # Bare upstream so `jj git push` works without network.
        _run(["git", "init", "--bare", str(upstream)], env=env)

        # Colocated jj repo + remote wiring.
        _run(["jj", "git", "init", "--colocate"], cwd=root, env=env)
        _run(
            ["jj", "config", "set", "--repo",
             "remotes.origin.auto-track-created-bookmarks", "glob:*"],
            cwd=root, env=env,
        )
        _run(["git", "remote", "add", "origin", str(upstream)], cwd=root, env=env)

        # Seed an initial commit on `main` and push so `main@origin` exists.
        (root / "README.md").write_text("# eval\n", encoding="utf-8")
        _run(["jj", "describe", "-m", "chore: seed"], cwd=root, env=env)
        _run(["jj", "bookmark", "create", "main", "-r", "@"], cwd=root, env=env)
        _run(["jj", "git", "push", "--bookmark", "main", "--allow-new"],
             cwd=root, env=env)
        # Create a fresh empty change on top so the working copy isn't `main` itself.
        _run(["jj", "new", "main"], cwd=root, env=env)

        repo = Repo(
            root=root, upstream=upstream, shim_dir=shim_dir,
            state_file=state_file, env=env,
        )
        # Sanity: shim is the gh on PATH.
        assert shutil.which("gh", path=env["PATH"]) == str(gh_shim), (
            f"gh shim not on PATH: which={shutil.which('gh', path=env['PATH'])}"
        )
        yield repo
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def execute_stack(
    repo: Repo,
    proposal: dict,
    *,
    fix_up: bool = False,
    expect_failure: bool = False,
) -> tuple[int, str, str]:
    """Run execute-stack.py against `proposal`. Returns (rc, stdout, stderr)."""
    proposal_path = repo.root / "_proposal.json"
    proposal_path.write_text(json.dumps(proposal), encoding="utf-8")
    cmd = [sys.executable, str(EXECUTE_STACK), "--proposal", str(proposal_path), "--yes"]
    if fix_up:
        cmd.append("--fix-up")
    res = _run(cmd, cwd=repo.root, env=repo.env, check=not expect_failure)
    return res.returncode, res.stdout, res.stderr


def jj_commit_count_on_bookmark(repo: Repo, bookmark: str, base: str = "main") -> int:
    """Count commits on `bookmark` excluding `base` (i.e. unique-to-bookmark commits)."""
    res = jj(
        repo, "log", "-r", f"{base}..{bookmark}", "--no-graph",
        "-T", "self.change_id().short() ++ \"\\n\"",
        check=True,
    )
    return len([line for line in res.stdout.splitlines() if line.strip()])


def jj_tip_change_id(repo: Repo, bookmark: str) -> str:
    res = jj(repo, "log", "-r", bookmark, "--no-graph",
             "-T", "self.change_id().short()")
    return res.stdout.strip()


def jj_tip_commit_id(repo: Repo, bookmark: str) -> str:
    res = jj(repo, "log", "-r", bookmark, "--no-graph",
             "-T", "self.commit_id().short()")
    return res.stdout.strip()


def jj_parent_change_id(repo: Repo, bookmark: str) -> str:
    """Change_id of the parent of `bookmark`'s tip commit."""
    res = jj(repo, "log", "-r", f"{bookmark}-", "--no-graph",
             "-T", "self.change_id().short()")
    return res.stdout.strip()


def jj_change_exists(repo: Repo, change_id: str) -> bool:
    """True if a change with this id is still in the repo (un-rewritten)."""
    res = jj(repo, "log", "-r", change_id, "--no-graph", "-T", "\"x\"", check=False)
    return res.returncode == 0 and "x" in res.stdout


def jj_op_count(repo: Repo) -> int:
    res = jj(repo, "op", "log", "--no-graph", "-T", "\"x\\n\"")
    return len([ln for ln in res.stdout.splitlines() if ln.strip()])


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"  ok  {msg}")


def assert_eq(got, want, label: str) -> None:
    if got != want:
        fail(f"{label}: got {got!r}, want {want!r}")
    ok(f"{label} == {want!r}")


def assert_true(cond: bool, label: str) -> None:
    if not cond:
        fail(label)
    ok(label)


def assert_ne(got, bad, label: str) -> None:
    if got == bad:
        fail(f"{label}: value unchanged ({got!r})")
    ok(f"{label}: changed ({bad!r} -> {got!r})")


def parse_stdout_json(stdout: str) -> dict:
    """execute-stack.py emits a single JSON object on stdout — parse it tolerantly."""
    text = stdout.strip()
    # The script may print other lines; find the first '{' and parse from there.
    idx = text.find("{")
    if idx == -1:
        fail(f"no JSON object in stdout:\n{stdout}")
    return json.loads(text[idx:])


def initial_two_pr_proposal() -> dict:
    """Two stacked PRs sharing a slug: lower owns lower.txt, upper owns upper.txt."""
    return {
        "slug": "demo",
        "base": "main@origin",
        "prs": [
            {
                "n": 1, "scope": "lower",
                "files": ["lower.txt"], "loc": 1,
                "bookmark": "demo/01-lower",
                "summary": "add lower",
                "title": "feat(lower): add lower file",
            },
            {
                "n": 2, "scope": "upper",
                "files": ["upper.txt"], "loc": 1,
                "bookmark": "demo/02-upper",
                "summary": "add upper",
                "title": "feat(upper): add upper file",
            },
        ],
    }


def seed_initial_files(repo: Repo) -> None:
    """Create the two files referenced by `initial_two_pr_proposal()`."""
    (repo.root / "lower.txt").write_text("v1\n", encoding="utf-8")
    (repo.root / "upper.txt").write_text("v1\n", encoding="utf-8")


def edit_lower_file(repo: Repo) -> None:
    """Edit the lower bookmark's file in the working copy."""
    (repo.root / "lower.txt").write_text("v2\n", encoding="utf-8")


def setup_initial_stack(repo: Repo) -> None:
    """Seed two files, run execute-stack to create the initial 2-PR stack."""
    seed_initial_files(repo)
    rc, _, _ = execute_stack(repo, initial_two_pr_proposal(), fix_up=False)
    if rc != 0:
        fail(f"initial stack creation failed with rc={rc}")
    # After execute-stack, `@` is left as a fresh empty change descending from
    # the top of the stack (jj split's residual). That mirrors what a real user
    # would have when starting follow-up edits, so we leave it alone.
