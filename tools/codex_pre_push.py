"""Review committed changes before push and block on findings or audit failures."""

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

import audit_db


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / ".codex" / "audit-reports"
PENDING = REPORTS / "pending"
ZERO = "0" * 40
REVIEW_SUFFIXES = {".md", ".py", ".ipynb", ".lean", ".rs", ".toml", ".yaml", ".yml", ".sh", ".ps1"}
REVIEW_NAMES = {"AGENTS.md", "Dockerfile", "Makefile"}
AUDIT_VERSION = "sqlite-workflow-v1"
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "line": {"type": "integer"},
                    "category": {"type": "string"},
                    "problem": {"type": "string"},
                    "evidence": {"type": "string"},
                    "correction": {"type": "string"},
                },
                "required": ["path", "line", "category", "problem", "evidence", "correction"],
                "additionalProperties": False,
            },
        },
        "checked": {"type": "array", "items": {"type": "string"}},
        "unverified": {"type": "array", "items": {"type": "string"}},
        "claims": {
            "type": "array", "items": {
                "type": "object", "properties": {
                    "path": {"type": "string"}, "line": {"type": "integer"},
                    "statement": {"type": "string"},
                    "evidence_type": {"type": "string", "enum": ["derivation", "numeric", "citation", "unverified"]},
                    "evidence_ref": {"type": "string"},
                    "assessment": {"type": "string", "enum": ["supported", "needs_check", "unsupported"]},
                },
                "required": ["path", "line", "statement", "evidence_type", "evidence_ref", "assessment"],
                "additionalProperties": False,
            },
        },
        "resolutions": {
            "type": "array", "items": {
                "type": "object", "properties": {
                    "prior_finding_id": {"type": "integer"},
                    "status": {"type": "string", "enum": ["resolved", "persists", "obsolete"]},
                    "evidence": {"type": "string"},
                },
                "required": ["prior_finding_id", "status", "evidence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["findings", "checked", "unverified", "claims", "resolutions"],
    "additionalProperties": False,
}


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


def empty_tree() -> str:
    result = subprocess.run(
        ["git", "hash-object", "-t", "tree", "-w", "--stdin"],
        cwd=ROOT, input=b"", capture_output=True, check=True,
    )
    return result.stdout.decode().strip()


def changes(base: str | None, head: str) -> tuple[list[str], str]:
    if base is None:
        raw = git("ls-tree", "-r", "--name-only", "-z", head).stdout
        names = [p for p in raw.decode("utf-8").split("\0") if p]
        base = empty_tree()
    else:
        raw = git("diff", "--name-only", "-z", "--find-renames", base, head).stdout
        names = [p for p in raw.decode("utf-8").split("\0") if p]
    selected = sorted({p for p in names if reviewable(p)})
    if not selected:
        return [], ""
    patch = git("diff", "--no-ext-diff", "--find-renames", base, head, "--", *selected).stdout.decode(
        "utf-8", errors="replace"
    )
    return selected, patch


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


def resolve_commit(ref: str) -> str:
    """Resolve a ref such as HEAD~1 to a commit ID, so audit keys never depend on a moving name."""
    return git("rev-parse", "--verify", f"{ref}^{{commit}}").stdout.decode().strip()


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


def validate_answer(value: object, files: list[str], prior_ids: set[int] | None = None) -> dict:
    if not isinstance(value, dict) or set(value) != {"findings", "checked", "unverified", "claims", "resolutions"}:
        raise ValueError("Codex returned an invalid audit response")
    findings, checked, unverified, claims, resolutions = (value[key] for key in (
        "findings", "checked", "unverified", "claims", "resolutions"))
    if any(not isinstance(items, list) for items in (findings, checked, unverified, claims, resolutions)):
        raise ValueError("Codex returned invalid audit lists")
    if not checked or any(not isinstance(item, str) or not item.strip() for item in checked + unverified):
        raise ValueError("Codex did not describe what it checked")
    for finding in findings:
        if not isinstance(finding, dict) or set(finding) != {
            "path", "line", "category", "problem", "evidence", "correction"
        }:
            raise ValueError("Codex returned an incomplete finding")
        if finding["path"] not in files or type(finding["line"]) is not int or finding["line"] < 1:
            raise ValueError("Codex finding does not point to a changed file and line")
        if any(not isinstance(finding[key], str) or not finding[key].strip() for key in (
            "category", "problem", "evidence", "correction"
        )):
            raise ValueError("Codex returned an incomplete finding")
    for claim in claims:
        if not isinstance(claim, dict) or set(claim) != {
            "path", "line", "statement", "evidence_type", "evidence_ref", "assessment"
        }:
            raise ValueError("Codex returned an incomplete claim")
        if claim["path"] not in files or type(claim["line"]) is not int or claim["line"] < 1:
            raise ValueError("Codex claim does not point to a changed file and line")
        if claim["evidence_type"] not in {"derivation", "numeric", "citation", "unverified"} or claim[
            "assessment"] not in {"supported", "needs_check", "unsupported"
        } or any(not isinstance(claim[key], str) or not claim[key].strip() for key in (
            "statement", "evidence_ref")):
            raise ValueError("Codex returned an invalid claim")
    expected = prior_ids or set()
    seen = set()
    for resolution in resolutions:
        if not isinstance(resolution, dict) or set(resolution) != {"prior_finding_id", "status", "evidence"}:
            raise ValueError("Codex returned an incomplete resolution")
        identifier = resolution["prior_finding_id"]
        if type(identifier) is not int or identifier not in expected or identifier in seen or resolution[
            "status"] not in {"resolved", "persists", "obsolete"
        } or not isinstance(resolution["evidence"], str) or not resolution["evidence"].strip():
            raise ValueError("Codex returned an invalid resolution")
        seen.add(identifier)
    if seen != expected:
        raise ValueError("Codex did not resolve every prior finding")
    if any(item["assessment"] == "unsupported" for item in claims) and not findings:
        raise ValueError("Unsupported claim must also be reported as a finding")
    return value


def blocking(answer: dict) -> bool:
    return bool(answer["findings"] or any(
        item["status"] == "persists" for item in answer["resolutions"]
    ) or any(item["assessment"] == "unsupported" for item in answer["claims"]))


def render_report(label: str, base: str | None, head: str, files: list[str], answer: dict) -> str:
    lines = [
        f"# Codex audit: {label}", "", f"Head: `{head}`  ", f"Base: `{base or 'root'}`",
        "", "Scope: committed changes listed below; CSV and generated results excluded.", "",
        *(f"- `{path}`" for path in files), "", "## 判定", "",
        "push を中断: 要対応" if blocking(answer) else "push 可: 指摘なし", "",
        "## 指摘", "",
    ]
    if answer["findings"]:
        for finding in answer["findings"]:
            lines.extend([
                f"- `{finding['path']}:{finding['line']}` ({finding['category']}): {finding['problem']}",
                f"  - 根拠: {finding['evidence']}",
                f"  - 修正案: {finding['correction']}",
            ])
    else:
        lines.append("なし")
    lines.extend(["", "## 主要な主張と根拠", ""])
    lines.extend(
        f"- `{item['path']}:{item['line']}` {item['statement']} — "
        f"{item['evidence_type']}/{item['assessment']}: {item['evidence_ref']}"
        for item in answer["claims"]
    )
    if not answer["claims"]:
        lines.append("なし")
    lines.extend(["", "## 前回指摘の再監査", ""])
    lines.extend(
        f"- #{item['prior_finding_id']} {item['status']}: {item['evidence']}"
        for item in answer["resolutions"]
    )
    if not answer["resolutions"]:
        lines.append("なし")
    lines.extend(["", "## 確認したこと", "", *(f"- {item}" for item in answer["checked"]),
                  "", "## 未確認", ""])
    lines.extend(f"- {item}" for item in answer["unverified"])
    if not answer["unverified"]:
        lines.append("なし")
    return "\n".join(lines) + "\n"


def load_cached(key: str, verdict: Path, files: list[str], db_path: Path | None = None) -> dict:
    """Validate a saved verdict against the prior findings stored with that audit record."""
    data = json.loads(verdict.read_text(encoding="utf-8"))
    db = audit_db.connect(db_path)
    try:
        record = db.execute("SELECT id, status FROM audits WHERE audit_key=?", (key,)).fetchone()
        stored_ids = set() if record is None else {
            row[0] for row in db.execute(
                "SELECT prior_finding_id FROM resolutions WHERE audit_id=?", (record["id"],))}
    finally:
        db.close()
    if record is None:
        raise ValueError("SQLite audit record is missing")
    cached = validate_answer(data, files, stored_ids)
    if record["status"] != ("findings" if blocking(cached) else "pass"):
        raise ValueError("SQLite audit record is inconsistent")
    return cached


def audit(base: str | None, head: str, dry_run: bool, scope: str = "manual") -> bool:
    files, patch = changes(base, head)
    label = f"{(base or 'root')[:12]}..{head[:12]}"
    if not files:
        print(f"Codex audit skipped ({label}): no reviewable changes")
        return True
    key = hashlib.sha256((AUDIT_VERSION + scope + (base or "root") + head + "\n".join(files)).encode()).hexdigest()[:16]
    report = REPORTS / f"{head[:12]}-{key}.md"
    verdict = REPORTS / f"{head[:12]}-{key}.json"
    if dry_run:
        print(f"Codex audit would review {label}: {', '.join(files)}")
        return True
    db = audit_db.connect()
    try:
        prior_id, prior_findings = audit_db.previous_findings(db, scope, base, head)
    finally:
        db.close()
    prior_ids = {item["id"] for item in prior_findings}

    def pending(reason: str) -> bool:
        db = audit_db.connect()
        try:
            audit_db.save_audit(db, key, scope, base, head, prior_id, "error", None, error=reason)
        finally:
            db.close()
        print(f"Codex audit pending ({label}): {reason}", file=sys.stderr)
        return False

    if report.exists() and verdict.exists():
        try:
            cached = load_cached(key, verdict, files)
        except (ValueError, json.JSONDecodeError):
            print(f"Codex audit cache invalid; rerunning: {report}", file=sys.stderr)
        else:
            print(f"Codex audit cached: {report}")
            if blocking(cached):
                print(f"Push blocked: audit needs attention; see {report}", file=sys.stderr)
            return not blocking(cached)

    executable = shutil.which("codex.cmd" if os.name == "nt" else "codex")
    if executable is None:
        return pending("Codex CLI is unavailable")
    REPORTS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="codex-push-audit-") as temp:
        snapshot = Path(temp) / "snapshot"
        snapshot.mkdir()
        extract_snapshot(head, snapshot)
        patch_file = snapshot / "AUDIT_CHANGESET.patch"
        patch_file.write_text(patch, encoding="utf-8")
        answer = Path(temp) / "answer.json"
        schema = Path(temp) / "schema.json"
        schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
        prompt = (
            "Read AUDIT_CHANGESET.patch and review only the listed changed files. "
            "Inspect the complete changed files to understand the before/after context, but report "
            "findings only at lines in changed files affected by this patch. "
            "Use other committed files to check assumptions, references, and related implementation. "
            "CSV files and generated experiment results are outside audit scope. "
            "Do not edit files. Review mathematical, scientific, and code correctness. "
            "For changed research notes, read docs/note_style.md and docs/concepts.md. Also audit "
            "the explanation as a first-time reader: prerequisites and symbols defined before use; "
            "claims and equations in a traceable order; each nontrivial equality justified; "
            "new concepts motivated and explained; examples that can be followed; consistent "
            "terminology; conclusions no broader than their evidence. For other changed prose, "
            "check argument structure, unsupported claims, and clarity that affects understanding. "
            "Report concrete, actionable defects only, not taste or minor wording preferences. "
            "Each finding needs a changed path and current line, category, specific problem, "
            "evidence or a precise explanation of the reading gap, and a suggested correction. "
            "Do not invent findings. Put no findings in an empty array. In checked, state the "
            "specific sections and review aspects checked; in unverified, state material limits. "
            "For changed research notes, list major added or revised claims in claims. For each, "
            "classify its evidence as derivation, numeric, citation, or unverified, identify the "
            "specific evidence location or missing evidence, and assess supported, needs_check, "
            "or unsupported. An unsupported claim must also be reported as a finding. "
            "For non-note changes, claims may be empty. "
            "If prior findings are supplied, inspect the new version for every one and return "
            "exactly one resolution per prior_finding_id: resolved, persists, or obsolete, with "
            "concrete evidence. Do not repeat an unchanged prior issue as a new finding. "
            "Take the author's response as a claim to check, not as proof. "
            "A persistent prior finding blocks push even if no new finding is emitted. "
            "Findings block this push. Answer in Japanese using the supplied JSON schema.\n\n"
            f"Range: {label}\nChanged files:\n" + "\n".join(f"- {p}" for p in files)
            + "\nPrior findings and Claude Code responses:\n"
            + json.dumps(prior_findings, ensure_ascii=False)
        )
        print(f"Codex audit running ({label}, {len(files)} files; up to 15 minutes)", file=sys.stderr, flush=True)
        try:
            result = subprocess.run(
                [executable, "exec", "--skip-git-repo-check", "--sandbox", "read-only",
                 "--output-schema", str(schema), "--output-last-message", str(answer), "-"],
                cwd=snapshot, input=prompt, text=True, encoding="utf-8", errors="replace",
                capture_output=True, timeout=900, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return pending(str(error))
        if result.returncode != 0 or not answer.exists() or not answer.read_text(encoding="utf-8").strip():
            return pending(f"Codex exited {result.returncode}; retry on a later push")
        try:
            parsed = validate_answer(json.loads(answer.read_text(encoding="utf-8")), files, prior_ids)
        except (ValueError, json.JSONDecodeError) as error:
            return pending(str(error))
        db = audit_db.connect()
        try:
            audit_id = audit_db.save_audit(db, key, scope, base, head, prior_id,
                                          "findings" if blocking(parsed) else "pass", report, parsed)
        finally:
            db.close()
        try:
            report.write_text(render_report(label, base, head, files, parsed)
                              + f"\nSQLite audit ID: #{audit_id}\n", encoding="utf-8")
            verdict.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as error:
            db = audit_db.connect()
            try:
                audit_db.mark_error(db, audit_id, str(error))
            finally:
                db.close()
            return pending(f"could not write the audit report: {error}")
        print(f"Codex audit report: {report}")
        print(f"Codex audit record: #{audit_id}")
        if blocking(parsed):
            print(f"Push blocked: audit needs attention; see {report}", file=sys.stderr)
            if any(item["status"] == "persists" and next(
                (prior["review_rounds"] for prior in prior_findings
                 if prior["id"] == item["prior_finding_id"]), 0
            ) >= 1 for item in parsed["resolutions"]):
                print("The same finding remains after two review rounds; request a human decision.", file=sys.stderr)
            return False
        return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--range", nargs=2, metavar=("BASE", "HEAD"), help="Inspect a range without Git hook stdin")
    parser.add_argument("--remote", default="unknown", help="Remote name or URL supplied by Git's pre-push hook")
    args = parser.parse_args()
    pairs: list[tuple[str | None, str, Path | None]] = []
    if args.range:
        try:
            pairs.append((resolve_commit(args.range[0]), resolve_commit(args.range[1]), None))
        except subprocess.CalledProcessError:
            print(f"Codex audit: cannot resolve --range {args.range[0]} {args.range[1]}", file=sys.stderr)
            return 1
    else:
        for line in sys.stdin:
            parts = line.split()
            if len(parts) != 4 or parts[1] == ZERO:
                continue
            head, remote_sha, remote_ref = parts[1], parts[3], parts[2]
            base = base_for_new_ref(head) if remote_sha == ZERO else remote_sha
            pairs.append((base, head, pending_file(args.remote, remote_ref)))
    seen: set[tuple[str | None, str, Path | None]] = set()
    all_passed = True
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
            scope = state_file.stem if state_file is not None else "manual"
            success = audit(base, head, args.dry_run, scope)
            all_passed = all_passed and success
            if success and state_file is not None and not args.dry_run:
                state_file.unlink(missing_ok=True)
        except (OSError, subprocess.CalledProcessError, ValueError, KeyError, json.JSONDecodeError) as error:
            print(f"Codex audit pending ({head[:12]}): {error}", file=sys.stderr)
            all_passed = False
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
