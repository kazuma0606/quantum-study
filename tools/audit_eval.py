"""Run opt-in Codex audit cases in isolated temporary Git repositories."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from unittest.mock import patch

import audit_db
import codex_pre_push as hook


ROOT = Path(__file__).resolve().parents[1]
CASES = Path(__file__).with_name("audit_eval_cases.json")


JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"matches": {"type": "boolean"}, "reason": {"type": "string"}},
    "required": ["matches", "reason"],
    "additionalProperties": False,
}


def codex_judge(finding: dict, expected_defect: str) -> tuple[bool, str]:
    """Ask Codex whether one finding addresses the expected defect. Never guesses on failure."""
    executable = shutil.which("codex.cmd" if os.name == "nt" else "codex")
    if executable is None:
        raise RuntimeError("Codex CLI is unavailable for judging")
    prompt = (
        "次の「指摘」が、「期待する欠陥」を扱っているかを判定してください。指摘が、期待する欠陥と同じ問題を"
        "具体的に述べていれば true、別の問題を述べている、または語が似ているだけなら false です。"
        "reason に理由を1文で書いてください。\n\n"
        f"期待する欠陥：{expected_defect}\n\n"
        f"指摘：{finding['problem']}\n根拠：{finding['evidence']}\n"
    )
    with tempfile.TemporaryDirectory(prefix="codex-eval-judge-") as directory:
        schema = Path(directory) / "schema.json"
        answer = Path(directory) / "answer.json"
        schema.write_text(json.dumps(JUDGE_SCHEMA), encoding="utf-8")
        result = subprocess.run(
            [executable, "exec", "--skip-git-repo-check", "--sandbox", "read-only",
             "--output-schema", str(schema), "--output-last-message", str(answer), "-"],
            cwd=directory, input=prompt, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=300, check=False,
        )
        if result.returncode != 0 or not answer.exists():
            raise RuntimeError(f"Codex judge exited {result.returncode}")
        value = json.loads(answer.read_text(encoding="utf-8"))
    if not isinstance(value.get("matches"), bool) or not isinstance(value.get("reason"), str):
        raise RuntimeError("Codex judge returned an invalid answer")
    return value["matches"], value["reason"]


def cached_judge(db: sqlite3.Connection, case_name: str, judge) -> "callable":
    """Wrap a judge so each (finding, case) pair is asked once and then read from SQLite."""
    def judged(finding: dict, expected_defect: str) -> tuple[bool, str]:
        defect_hash = hashlib.sha256(expected_defect.encode("utf-8")).hexdigest()[:16]
        row = db.execute("SELECT matched, reason FROM eval_matches "
                         "WHERE finding_id=? AND case_name=? AND defect_hash=?",
                         (finding["id"], case_name, defect_hash)).fetchone()
        if row is not None:
            return bool(row["matched"]), row["reason"]
        matched, reason = judge(finding, expected_defect)
        with db:
            db.execute("INSERT INTO eval_matches(finding_id,case_name,defect_hash,matched,reason) "
                       "VALUES(?,?,?,?,?)", (finding["id"], case_name, defect_hash, int(matched), reason))
        return matched, reason
    return judged


def score(findings: list[dict], expected_defect: str | None, judge) -> dict[str, int]:
    """Judge each finding against the expected defect. A safe case counts every finding as false."""
    if not expected_defect:
        return {"tp": 0, "fn": 0, "fp": len(findings), "tn": int(not findings)}
    hits = [judge(item, expected_defect)[0] for item in findings]
    return {"tp": int(any(hits)), "fn": int(not any(hits)),
            "fp": hits.count(False), "tn": 0}


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True)
    return result.stdout.decode().strip()


def run_case(case: dict) -> dict:
    with tempfile.TemporaryDirectory(prefix="codex-audit-eval-") as directory:
        repo = Path(directory)
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Audit Eval")
        git(repo, "config", "user.email", "audit-eval@example.invalid")
        for name in ("note_style.md", "concepts.md"):
            source = ROOT / "docs" / name
            target = repo / "docs" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        note = repo / "研究ノート" / "eval.md"
        note.parent.mkdir(parents=True)
        note.write_text(case["base"], encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "baseline")
        base = git(repo, "rev-parse", "HEAD")
        note.write_text(case["changed"], encoding="utf-8")
        git(repo, "commit", "-qam", "candidate")
        head = git(repo, "rev-parse", "HEAD")
        scope = f"eval:{case['name']}"
        with patch.object(hook, "ROOT", repo):
            hook.audit(base, head, False, scope)
        db = audit_db.connect()
        try:
            audit = db.execute("""
                SELECT id,status,report_path FROM audits
                WHERE scope=? AND head_sha=? ORDER BY id DESC LIMIT 1
            """, (scope, head)).fetchone()
            if audit is None or audit["status"] == "error":
                raise RuntimeError(f"Codex evaluation failed for {case['name']}")
            findings = [dict(row) for row in db.execute(
                "SELECT id,problem,evidence,line FROM findings WHERE audit_id=? ORDER BY id", (audit["id"],))]
            return {"case": case["name"], "audit_id": audit["id"],
                    "report": audit["report_path"], "findings": len(findings),
                    **score(findings, case.get("expected_defect"),
                           cached_judge(db, case["name"], codex_judge))}
        finally:
            db.close()


def run_regression() -> dict:
    """Exercise the full bad claim -> response -> fixed claim review chain."""
    case = next(item for item in json.loads(CASES.read_text(encoding="utf-8"))
                if item["name"] == "endpoint_counterexample")
    with tempfile.TemporaryDirectory(prefix="codex-audit-regression-") as directory:
        repo = Path(directory)
        git(repo, "init", "-q")
        git(repo, "config", "user.name", "Audit Eval")
        git(repo, "config", "user.email", "audit-eval@example.invalid")
        for name in ("note_style.md", "concepts.md"):
            target = repo / "docs" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / "docs" / name).read_bytes())
        note = repo / "研究ノート" / "eval.md"
        note.parent.mkdir(parents=True)
        note.write_text(case["base"], encoding="utf-8")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "baseline")
        base = git(repo, "rev-parse", "HEAD")
        note.write_text(case["changed"], encoding="utf-8")
        git(repo, "commit", "-qam", "incorrect endpoint")
        bad_head = git(repo, "rev-parse", "HEAD")
        scope = "eval:regression_endpoints"
        with patch.object(hook, "ROOT", repo):
            hook.audit(base, bad_head, False, scope)
        db = audit_db.connect()
        try:
            first = db.execute("SELECT id,status FROM audits WHERE scope=? AND head_sha=?",
                               (scope, bad_head)).fetchone()
            if first is None or first["status"] != "findings":
                raise RuntimeError("Initial regression case did not produce a finding")
            finding = db.execute("SELECT id FROM findings WHERE audit_id=? ORDER BY id LIMIT 1",
                                 (first["id"],)).fetchone()
            if finding is None:
                raise RuntimeError("Initial regression case did not record a finding")
            with db:
                db.execute("""
                    INSERT INTO responses(finding_id,decision,rationale,evidence_ref,actor)
                    VALUES(?,?,?,?,?)
                """, (finding["id"], "fix", "端点で等号が成り立つよう修正した",
                      "研究ノート/eval.md:7", "eval fixture"))
        finally:
            db.close()
        note.write_text(
            case["base"] + "\n平面の原点を中心とする半径1の円を単位円とする。正の横軸から反時計回りに角度 "
            "$\\theta$ を測り、円周上の点の縦座標を $\\sin\\theta$ と定義する。\n\n"
            "$0\\le\\theta\\le\\pi$ では点は上半円上にあるので、縦座標は0以上である。\n\n"
            "$$\\sin\\theta\\ge 0$$\n\n"
            "両端点では縦座標は0であり、$\\theta=\\pi/2$ では1である。\n",
            encoding="utf-8",
        )
        git(repo, "commit", "-qam", "fix endpoint")
        fixed_head = git(repo, "rev-parse", "HEAD")
        with patch.object(hook, "ROOT", repo):
            passed = hook.audit(base, fixed_head, False, scope)
        db = audit_db.connect()
        try:
            second = db.execute("SELECT id,status,report_path FROM audits WHERE scope=? AND head_sha=?",
                                (scope, fixed_head)).fetchone()
            if second is None:
                raise RuntimeError("Follow-up regression audit was not recorded")
            resolution = db.execute("""
                SELECT status,evidence FROM resolutions WHERE audit_id=? AND prior_finding_id=?
            """, (second["id"], finding["id"])).fetchone()
            return {"initial_audit_id": first["id"], "followup_audit_id": second["id"],
                    "finding_id": finding["id"], "followup_passed": passed,
                    "resolution": dict(resolution) if resolution else None,
                    "report": second["report_path"]}
        finally:
            db.close()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="Run one named case; default runs all cases")
    parser.add_argument("--summary", action="store_true", help="Show the latest stored result for each case")
    parser.add_argument("--regression", action="store_true", help="Run bad claim, response, and fix chain")
    args = parser.parse_args()
    if args.regression:
        result = run_regression()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["followup_passed"] and result["resolution"] and result["resolution"]["status"] == "resolved" else 1
    if args.summary:
        db = audit_db.connect()
        try:
            rows = db.execute("SELECT cases_json FROM eval_runs ORDER BY id DESC").fetchall()
            latest = {}
            for row in rows:
                for result in json.loads(row["cases_json"]):
                    latest.setdefault(result["case"], result)
            totals = {key: sum(result[key] for result in latest.values())
                      for key in ("tp", "fn", "fp", "tn")}
            print(json.dumps({"totals": totals, "cases": list(latest.values())},
                             ensure_ascii=False, indent=2))
            return 0
        finally:
            db.close()
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    if args.case:
        cases = [case for case in cases if case["name"] == args.case]
        if not cases:
            parser.error(f"unknown case: {args.case}")
    results = [run_case(case) for case in cases]
    totals = {key: sum(result[key] for result in results) for key in ("tp", "fn", "fp", "tn")}
    db = audit_db.connect()
    try:
        with db:
            cursor = db.execute("""
                INSERT INTO eval_runs(cases_json,true_positive,false_negative,false_positive,true_negative)
                VALUES(?,?,?,?,?)
            """, (json.dumps(results, ensure_ascii=False),
                  totals["tp"], totals["fn"], totals["fp"], totals["tn"]))
        print(json.dumps({"eval_run_id": cursor.lastrowid, "totals": totals, "cases": results},
                         ensure_ascii=False, indent=2))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
