"""Review the committed content about to be pushed, leaving a local report.

Git supplies ref updates on stdin. This script never decides whether a push is
allowed; failures remain pending and can be retried by a later push.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / ".codex" / "audit-reports"
PENDING = REPORTS / "pending"
ZERO = "0" * 40
REVIEW_SUFFIXES = {".md", ".py", ".ipynb", ".lean", ".rs", ".toml", ".yaml", ".yml", ".sh", ".ps1"}
REVIEW_NAMES = {"AGENTS.md", "Dockerfile", "Makefile"}


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=check)


def reviewable(path: str) -> bool:
    name = Path(path).name
    if path.lower().endswith(".csv"):
        return False
    if "/results/" in f"/{path}/":
        return False
    return name in REVIEW_NAMES or Path(name).suffix.lower() in REVIEW_SUFFIXES


def base_for_new_ref(head: str) -> str | None:
    for ref in ("refs/remotes/origin/HEAD", "refs/remotes/origin/main", "refs/remotes/origin/master"):
        result = git("merge-base", head, ref, check=False)
        if result.returncode == 0:
            return result.stdout.decode().strip()
    result = git("rev-parse", f"{head}^", check=False)
    return result.stdout.decode().strip() if result.returncode == 0 else None


def changes(base: str | None, head: str) -> tuple[list[str], str]:
    if base is None:
        raw = git("ls-tree", "-r", "--name-only", "-z", head).stdout
        names = [p for p in raw.decode("utf-8").split("\0") if p]
        diff_args = ("show", "--format=", "--no-ext-diff", "--find-renames", "-w", "--ignore-blank-lines", head)
    else:
        raw = git("diff", "--name-only", "-z", "--find-renames", base, head).stdout
        names = [p for p in raw.decode("utf-8").split("\0") if p]
        diff_args = ("diff", "--no-ext-diff", "--find-renames", "-w", "--ignore-blank-lines", base, head)
    selected = sorted({p for p in names if reviewable(p)})
    if not selected:
        return [], ""
    patch = git(*diff_args, "--", *selected).stdout.decode("utf-8", errors="replace")
    return selected, patch


def explicitly_style_only(base: str | None, head: str, files: list[str]) -> bool:
    if not files or any(Path(path).suffix.lower() != ".md" for path in files):
        return False
    rev_range = f"{base}..{head}" if base else head
    commits = [sha for sha in git("rev-list", rev_range).stdout.decode().splitlines() if sha]
    if not commits:
        return False
    return all(
        re.search(r"(?im)^Audit-Skip:\s*style\s*$", git("log", "-1", "--format=%B", sha).stdout.decode("utf-8"))
        for sha in commits
    )


def extract_snapshot(head: str, target: Path) -> None:
    archive = git("archive", "--format=tar", head).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        for member in tar:
            if member.name.lower().endswith(".csv") or "/results/" in f"/{member.name}/":
                continue
            destination = (target / member.name).resolve()
            if not destination.is_relative_to(target.resolve()):
                raise ValueError(f"Unsafe archive path: {member.name}")
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                destination.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                if source is not None:
                    with source, destination.open("wb") as output:
                        shutil.copyfileobj(source, output)


def pending_file(remote_name: str, remote_ref: str) -> Path:
    key = hashlib.sha256(f"{remote_name}\n{remote_ref}".encode()).hexdigest()[:20]
    return PENDING / f"{key}.json"


def read_pending(path: Path) -> str | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))["base"]
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40,64}", value):
        raise ValueError(f"Invalid pending audit base: {path}")
    return value


def commit_exists(sha: str) -> bool:
    return git("cat-file", "-e", f"{sha}^{{commit}}", check=False).returncode == 0


def write_pending(path: Path, base: str | None) -> None:
    if base is None:
        # A root commit has no base; use ZERO as the persistent sentinel.
        base = ZERO
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False) as output:
        temporary = Path(output.name)
        json.dump({"base": base}, output)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def audit(base: str | None, head: str, dry_run: bool) -> bool:
    files, patch = changes(base, head)
    label = f"{(base or 'root')[:12]}..{head[:12]}"
    if not files:
        print(f"Codex audit skipped ({label}): no reviewable changes")
        return True
    if not patch.strip():
        print(f"Codex audit skipped ({label}): whitespace-only changes")
        return True
    if explicitly_style_only(base, head, files):
        print(f"Codex audit skipped ({label}): all Markdown commits have Audit-Skip: style")
        return True

    key = hashlib.sha256(((base or "root") + head + "\n".join(files)).encode()).hexdigest()[:16]
    report = REPORTS / f"{head[:12]}-{key}.md"
    if report.exists():
        print(f"Codex audit cached: {report}")
        return True
    if dry_run:
        print(f"Codex audit would review {label}: {', '.join(files)}")
        return True

    executable = shutil.which("codex.cmd" if os.name == "nt" else "codex")
    if executable is None:
        print("Codex audit pending: Codex CLI is unavailable", file=sys.stderr)
        return False
    REPORTS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex-push-audit-") as temp:
        snapshot = Path(temp) / "snapshot"
        snapshot.mkdir()
        extract_snapshot(head, snapshot)
        patch_file = snapshot / "AUDIT_CHANGESET.patch"
        patch_file.write_text(patch, encoding="utf-8")
        answer = Path(temp) / "answer.md"
        prompt = (
            "Read AUDIT_CHANGESET.patch and review only the listed changed files. "
            "Use other committed files only to check assumptions and references. "
            "CSV files and generated experiment results are outside audit scope. "
            "Do not edit files. Report only actionable mathematical, scientific, or code defects "
            "with path, line, evidence or counterexample, and a suggested correction. "
            "Distinguish verified findings from uncertainty; do not repeat stylistic observations. "
            "A finding is advice, not a push veto. Answer in Japanese.\n\n"
            f"Range: {label}\nChanged files:\n" + "\n".join(f"- {p}" for p in files)
        )
        print(f"Codex audit running ({label}, {len(files)} files; up to 15 minutes)", file=sys.stderr, flush=True)
        try:
            result = subprocess.run(
                [executable, "exec", "--skip-git-repo-check", "--sandbox", "read-only", "--output-last-message", str(answer), "-"],
                cwd=snapshot, input=prompt, text=True, encoding="utf-8", errors="replace",
                capture_output=True, timeout=900, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"Codex audit pending ({label}): {error}", file=sys.stderr)
            return False
        if result.returncode != 0 or not answer.exists() or not answer.read_text(encoding="utf-8").strip():
            print(f"Codex audit pending ({label}): Codex exited {result.returncode}; retry on a later push", file=sys.stderr)
            return False
        body = answer.read_text(encoding="utf-8")
        body = body.replace(snapshot.as_posix(), ROOT.as_posix()).replace(str(snapshot), str(ROOT))
        report.write_text(
            f"# Codex audit: {label}\n\nHead: `{head}`  \nBase: `{base or 'root'}`\n\n"
            "Scope: committed changes listed below; CSV and generated results excluded.\n\n"
            + "\n".join(f"- `{p}`" for p in files) + "\n\n---\n\n" + body + "\n",
            encoding="utf-8",
        )
        print(f"Codex audit report: {report}")
        return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--range", nargs=2, metavar=("BASE", "HEAD"), help="Inspect a range without Git hook stdin")
    parser.add_argument("--remote", default="unknown", help="Remote name or URL supplied by Git's pre-push hook")
    args = parser.parse_args()
    pairs: list[tuple[str | None, str, Path | None]] = []
    if args.range:
        pairs.append((args.range[0], args.range[1], None))
    else:
        for line in sys.stdin:
            parts = line.split()
            if len(parts) != 4 or parts[1] == ZERO:
                continue
            head, remote_sha, remote_ref = parts[1], parts[3], parts[2]
            base = base_for_new_ref(head) if remote_sha == ZERO else remote_sha
            pairs.append((base, head, pending_file(args.remote, remote_ref)))
    seen: set[tuple[str | None, str, Path | None]] = set()
    for current_base, head, state_file in pairs:
        if (current_base, head, state_file) in seen:
            continue
        seen.add((current_base, head, state_file))
        try:
            saved_base = read_pending(state_file) if state_file is not None else None
            if saved_base not in (None, ZERO) and not commit_exists(saved_base):
                print(
                    f"Codex audit: saved base {saved_base[:12]} is unavailable; reviewing only the current push range",
                    file=sys.stderr,
                )
                saved_base = None
            base = None if saved_base == ZERO else saved_base or current_base
            if state_file is not None and not args.dry_run:
                write_pending(state_file, base)
            success = audit(base, head, args.dry_run)
            if success and state_file is not None and not args.dry_run:
                state_file.unlink(missing_ok=True)
        except (OSError, subprocess.CalledProcessError, ValueError, KeyError, json.JSONDecodeError) as error:
            print(f"Codex audit pending ({head[:12]}): {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
