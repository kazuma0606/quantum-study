"""Inspect local audit history and record Claude Code's response to a finding."""

from __future__ import annotations

import argparse
import json
import sys

import audit_db


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("recent", help="Show recent audit runs")
    search = commands.add_parser("search", help="Search past findings and claims")
    search.add_argument("query")
    findings = commands.add_parser("findings", help="Show findings for an audit ID")
    findings.add_argument("audit_id", type=int)
    claims = commands.add_parser("claims", help="Show claims and evidence for an audit ID")
    claims.add_argument("audit_id", type=int)
    responses = commands.add_parser("responses", help="Show response and resolution history for a finding ID")
    responses.add_argument("finding_id", type=int)
    respond = commands.add_parser("respond", help="Record Claude Code's response; does not override the gate")
    respond.add_argument("finding_id", type=int)
    respond.add_argument("decision", choices=("fix", "dispute", "human"))
    respond.add_argument("--rationale", required=True)
    respond.add_argument("--evidence", required=True, help="A file:line, test result, or concrete counterexample")
    respond.add_argument("--actor", default="Claude Code")
    args = parser.parse_args()
    db = audit_db.connect()
    try:
        if args.command == "recent":
            rows = db.execute("""
                SELECT a.id,a.created_at,a.scope,a.status,a.base_sha,a.head_sha,a.report_path,
                       COUNT(f.id) AS finding_count
                FROM audits a LEFT JOIN findings f ON f.audit_id=a.id
                GROUP BY a.id ORDER BY a.id DESC LIMIT 20
            """).fetchall()
        elif args.command == "search":
            pattern = "%" + args.query.replace("%", "\\%").replace("_", "\\_") + "%"
            rows = db.execute("""
                SELECT 'finding' AS kind,id,path,line,category AS type,problem AS text,evidence
                FROM findings WHERE (problem LIKE ? ESCAPE '\\' OR evidence LIKE ? ESCAPE '\\'
                                     OR category LIKE ? ESCAPE '\\')
                UNION ALL
                SELECT 'claim',id,path,line,evidence_type,statement,evidence_ref
                FROM claims WHERE (statement LIKE ? ESCAPE '\\' OR evidence_ref LIKE ? ESCAPE '\\')
                LIMIT 50
            """, (pattern, pattern, pattern, pattern, pattern)).fetchall()
        elif args.command == "findings":
            rows = db.execute("SELECT * FROM findings WHERE audit_id=? ORDER BY id", (args.audit_id,)).fetchall()
        elif args.command == "claims":
            rows = db.execute("SELECT * FROM claims WHERE audit_id=? ORDER BY id", (args.audit_id,)).fetchall()
        elif args.command == "responses":
            rows = db.execute("""
                SELECT 'response' AS kind,id,decision AS status,rationale AS detail,
                       evidence_ref AS evidence,actor,created_at
                FROM responses WHERE finding_id=?
                UNION ALL
                SELECT 'resolution',id,status,evidence,evidence,'Codex',created_at
                FROM resolutions WHERE prior_finding_id=?
                ORDER BY created_at,id
            """, (args.finding_id, args.finding_id)).fetchall()
        else:
            exists = db.execute("SELECT 1 FROM findings WHERE id=?", (args.finding_id,)).fetchone()
            if exists is None:
                parser.error(f"finding #{args.finding_id} does not exist")
            if not args.rationale.strip() or not args.evidence.strip():
                parser.error("rationale and evidence must be nonempty")
            with db:
                cursor = db.execute("""
                    INSERT INTO responses(finding_id,decision,rationale,evidence_ref,actor)
                    VALUES(?,?,?,?,?)
                """, (args.finding_id, args.decision, args.rationale, args.evidence, args.actor))
            print(f"Recorded response #{cursor.lastrowid} for finding #{args.finding_id}")
            return 0
        print(json.dumps([dict(row) for row in rows], ensure_ascii=False, indent=2))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
