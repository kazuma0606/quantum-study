"""Local SQLite history for Codex reviews and Claude Code responses."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3


DEFAULT_DB = Path(__file__).resolve().parents[1] / ".codex" / "audit-reports" / "audit.sqlite3"


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or DEFAULT_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY,
            audit_key TEXT NOT NULL UNIQUE,
            scope TEXT NOT NULL,
            base_sha TEXT,
            head_sha TEXT NOT NULL,
            prior_audit_id INTEGER REFERENCES audits(id),
            status TEXT NOT NULL CHECK(status IN ('pass', 'findings', 'error')),
            report_path TEXT,
            checked_json TEXT NOT NULL DEFAULT '[]',
            unverified_json TEXT NOT NULL DEFAULT '[]',
            error TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY,
            audit_id INTEGER NOT NULL REFERENCES audits(id),
            path TEXT NOT NULL,
            line INTEGER NOT NULL,
            category TEXT NOT NULL,
            problem TEXT NOT NULL,
            evidence TEXT NOT NULL,
            correction TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY,
            finding_id INTEGER NOT NULL REFERENCES findings(id),
            decision TEXT NOT NULL CHECK(decision IN ('fix', 'dispute', 'human')),
            rationale TEXT NOT NULL,
            evidence_ref TEXT NOT NULL,
            actor TEXT NOT NULL DEFAULT 'Claude Code',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY,
            audit_id INTEGER NOT NULL REFERENCES audits(id),
            path TEXT NOT NULL,
            line INTEGER NOT NULL,
            statement TEXT NOT NULL,
            evidence_type TEXT NOT NULL CHECK(evidence_type IN ('derivation', 'numeric', 'citation', 'unverified')),
            evidence_ref TEXT NOT NULL,
            assessment TEXT NOT NULL CHECK(assessment IN ('supported', 'needs_check', 'unsupported'))
        );
        CREATE TABLE IF NOT EXISTS resolutions (
            id INTEGER PRIMARY KEY,
            audit_id INTEGER NOT NULL REFERENCES audits(id),
            prior_finding_id INTEGER NOT NULL REFERENCES findings(id),
            status TEXT NOT NULL CHECK(status IN ('resolved', 'persists', 'obsolete')),
            evidence TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(audit_id, prior_finding_id)
        );
        CREATE TABLE IF NOT EXISTS eval_runs (
            id INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            cases_json TEXT NOT NULL,
            true_positive INTEGER NOT NULL,
            false_negative INTEGER NOT NULL,
            false_positive INTEGER NOT NULL,
            true_negative INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_audits_chain ON audits(scope, base_sha, id);
        CREATE INDEX IF NOT EXISTS idx_findings_audit ON findings(audit_id);
        CREATE INDEX IF NOT EXISTS idx_responses_finding ON responses(finding_id, id);
    """)
    columns = {row["name"] for row in db.execute("PRAGMA table_info(resolutions)")}
    if "created_at" not in columns:
        with db:
            db.execute("ALTER TABLE resolutions ADD COLUMN created_at TEXT")
            db.execute("UPDATE resolutions SET created_at=CURRENT_TIMESTAMP WHERE created_at IS NULL")
    return db


def previous_findings(db: sqlite3.Connection, scope: str, base: str | None, head: str) -> tuple[int | None, list[dict]]:
    prior = db.execute(
        "SELECT id FROM audits WHERE scope=? AND base_sha IS ? AND head_sha<>? "
        "AND status='findings' ORDER BY id DESC LIMIT 1", (scope, base, head)
    ).fetchone()
    if prior is None:
        return None, []
    rows = db.execute("""
        SELECT f.*, r.decision, r.rationale, r.evidence_ref,
               (SELECT COUNT(*) FROM resolutions WHERE prior_finding_id=f.id) AS review_rounds
        FROM findings f LEFT JOIN responses r ON r.id=(
            SELECT MAX(id) FROM responses WHERE finding_id=f.id)
        WHERE f.audit_id=? OR f.id IN (
            SELECT prior_finding_id FROM resolutions WHERE audit_id=? AND status='persists'
        ) ORDER BY f.id
    """, (prior["id"], prior["id"])).fetchall()
    return prior["id"], [dict(row) for row in rows]


def save_audit(db: sqlite3.Connection, key: str, scope: str, base: str | None, head: str,
               prior_id: int | None, status: str, report: Path | None,
               answer: dict | None = None, error: str | None = None) -> int:
    answer = answer or {"findings": [], "claims": [], "resolutions": [], "checked": [], "unverified": []}
    with db:
        existing = db.execute("SELECT status FROM audits WHERE audit_key=?", (key,)).fetchone()
        if existing is not None and existing["status"] != "error":
            raise ValueError("Completed audit records are immutable; use a new audit version")
        db.execute("""
            INSERT INTO audits(audit_key,scope,base_sha,head_sha,prior_audit_id,status,report_path,
                               checked_json,unverified_json,error)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(audit_key) DO UPDATE SET status=excluded.status,
                report_path=excluded.report_path, checked_json=excluded.checked_json,
                unverified_json=excluded.unverified_json, error=excluded.error
        """, (key, scope, base, head, prior_id, status, str(report) if report else None,
              json.dumps(answer["checked"], ensure_ascii=False),
              json.dumps(answer["unverified"], ensure_ascii=False), error))
        audit_id = db.execute("SELECT id FROM audits WHERE audit_key=?", (key,)).fetchone()["id"]
        db.executemany("""
            INSERT INTO findings(audit_id,path,line,category,problem,evidence,correction)
            VALUES(?,?,?,?,?,?,?)
        """, [(audit_id, *(finding[k] for k in (
            "path", "line", "category", "problem", "evidence", "correction")))
               for finding in answer["findings"]])
        db.executemany("""
            INSERT INTO claims(audit_id,path,line,statement,evidence_type,evidence_ref,assessment)
            VALUES(?,?,?,?,?,?,?)
        """, [(audit_id, *(claim[k] for k in (
            "path", "line", "statement", "evidence_type", "evidence_ref", "assessment")))
               for claim in answer["claims"]])
        db.executemany("""
            INSERT INTO resolutions(audit_id,prior_finding_id,status,evidence,created_at)
            VALUES(?,?,?,?,CURRENT_TIMESTAMP)
        """, [(audit_id, resolution["prior_finding_id"], resolution["status"], resolution["evidence"])
               for resolution in answer["resolutions"]])
    return audit_id
