"""Review the committed content about to be pushed, leaving a local report.

Git supplies ref updates on stdin. This script never decides whether a push is
allowed; failures remain pending and can be retried by a later push.
"""

from __future__ import annotations

import argparse
import hashlib
import io
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
        diff_args = ("show", "--format=", "--no-ext-diff", "--find-renames", "-w", head)
    else:
        raw = git("diff", "--name-only", "-z", "--find-renames", base, head).stdout
        names = [p for p in raw.decode("utf-8").split("\0") if p]
        diff_args = ("diff", "--no-ext-diff", "--find-renames", "-w", base, head)
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


def audit(base: str | None, head: str, dry_run: bool) -> None:
    files, patch = changes(base, head)
    label = f"{(base or 'root')[:12]}..{head[:12]}"
    if not files:
        print(f"Codex audit skipped ({label}): no reviewable changes")
        return
    if not patch.strip():
        print(f"Codex audit skipped ({label}): whitespace-only changes")
        return
    if explicitly_style_only(base, head, files):
        print(f"Codex audit skipped ({label}): all Markdown commits have Audit-Skip: style")
        return

    key = hashlib.sha256(((base or "root") + head + "\n".join(files)).encode()).hexdigest()[:16]
    report = REPORTS / f"{head[:12]}-{key}.md"
    if report.exists():
        print(f"Codex audit cached: {report}")
        return
    if dry_run:
        print(f"Codex audit would review {label}: {', '.join(files)}")
        return

    executable = shutil.which("codex.cmd" if os.name == "nt" else "codex")
    if executable is None:
        print("Codex audit pending: Codex CLI is unavailable", file=sys.stderr)
        return
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
        try:
            result = subprocess.run(
                [executable, "exec", "--skip-git-repo-check", "--sandbox", "read-only", "--output-last-message", str(answer), "-"],
                cwd=snapshot, input=prompt, text=True, encoding="utf-8", errors="replace",
                capture_output=True, timeout=900, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"Codex audit pending ({label}): {error}", file=sys.stderr)
            return
        if result.returncode != 0 or not answer.exists() or not answer.read_text(encoding="utf-8").strip():
            print(f"Codex audit pending ({label}): Codex exited {result.returncode}; retry on a later push", file=sys.stderr)
            return
        body = answer.read_text(encoding="utf-8")
        body = body.replace(snapshot.as_posix(), ROOT.as_posix()).replace(str(snapshot), str(ROOT))
        report.write_text(
            f"# Codex audit: {label}\n\nHead: `{head}`  \nBase: `{base or 'root'}`\n\n"
            "Scope: committed changes listed below; CSV and generated results excluded.\n\n"
            + "\n".join(f"- `{p}`" for p in files) + "\n\n---\n\n" + body + "\n",
            encoding="utf-8",
        )
        print(f"Codex audit report: {report}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--range", nargs=2, metavar=("BASE", "HEAD"), help="Inspect a range without Git hook stdin")
    args = parser.parse_args()
    pairs: list[tuple[str | None, str]] = []
    if args.range:
        pairs.append((args.range[0], args.range[1]))
    else:
        for line in sys.stdin:
            parts = line.split()
            if len(parts) != 4 or parts[1] == ZERO:
                continue
            head, remote = parts[1], parts[3]
            base = base_for_new_ref(head) if remote == ZERO else remote
            pairs.append((base, head))
    seen: set[tuple[str | None, str]] = set()
    for base, head in pairs:
        if (base, head) in seen:
            continue
        seen.add((base, head))
        try:
            audit(base, head, args.dry_run)
        except (OSError, subprocess.CalledProcessError, ValueError) as error:
            print(f"Codex audit pending ({head[:12]}): {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
