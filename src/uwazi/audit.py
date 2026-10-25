"""Reviewer decisions and a hash-chained, tamper-evident audit log (SQLite)."""
from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from datetime import UTC, datetime

OUTCOMES = {
    "needs_info": "Needs more information",
    "explained_legit": "Explained as legitimate",
    "data_error": "Data error",
    "referred": "Refer to an oversight body",
    "no_action": "No action",
}


def _digest(prev, ts, actor, action, obj, detail) -> str:
    return hashlib.sha256("|".join([prev, ts, actor, action, obj, detail]).encode()).hexdigest()


class AuditLog:
    def __init__(self, path: str):
        self.path = path
        with closing(self._conn()) as c:
            c.execute("create table if not exists review(ts text, award_id text, reviewer text, outcome text, code text, notes text)")
            c.execute("create table if not exists audit(ts text, actor text, action text, obj text, detail text, prev text, hash text)")
            c.commit()

    def _conn(self):
        return sqlite3.connect(self.path)

    def append(self, actor: str, action: str, obj: str, detail: str) -> str:
        ts = datetime.now(UTC).isoformat(timespec="seconds")
        with closing(self._conn()) as c:
            row = c.execute("select hash from audit order by rowid desc limit 1").fetchone()
            prev = row[0] if row else ""
            h = _digest(prev, ts, actor, action, obj, detail)
            c.execute("insert into audit values (?,?,?,?,?,?,?)", (ts, actor, action, obj, detail, prev, h))
            c.commit()
        return h

    def record_review(self, award_id: str, reviewer: str, outcome: str, code: str = "", notes: str = "") -> None:
        if outcome not in OUTCOMES:
            raise ValueError(f"Unknown outcome: {outcome}")
        ts = datetime.now(UTC).isoformat(timespec="seconds")
        with closing(self._conn()) as c:
            c.execute("insert into review values (?,?,?,?,?,?)", (ts, award_id, reviewer, outcome, code, notes))
            c.commit()
        notes_hash = hashlib.sha256(notes.encode()).hexdigest()[:12]  # binds notes to the chain without exposing them
        self.append(reviewer, "review", award_id, f"{outcome}|{code}|notes:{notes_hash}")

    def verify(self) -> bool:
        with closing(self._conn()) as c:
            rows = c.execute("select ts,actor,action,obj,detail,prev,hash from audit order by rowid").fetchall()
        prev = ""
        for ts, actor, action, obj, detail, p, h in rows:
            if p != prev or _digest(p, ts, actor, action, obj, detail) != h:
                return False
            prev = h
        return True

    def entries(self, limit: int = 200) -> list[dict]:
        with closing(self._conn()) as c:
            rows = c.execute("select ts,actor,action,obj,detail,hash from audit order by rowid desc limit ?", (limit,)).fetchall()
        return [dict(zip(("ts", "actor", "action", "obj", "detail", "hash"), r, strict=True)) for r in rows]

    def latest_reviews(self) -> dict:
        with closing(self._conn()) as c:
            rows = c.execute("select award_id,outcome,code,notes,reviewer,ts from review order by rowid").fetchall()
        return {r[0]: dict(outcome=r[1], code=r[2], notes=r[3], reviewer=r[4], ts=r[5]) for r in rows}

    def tamper_for_demo(self) -> bool:
        """Edit the first entry directly in the database to demonstrate tamper detection."""
        with closing(self._conn()) as c:
            cur = c.execute("update audit set detail = detail || ' (edited)' where rowid = (select min(rowid) from audit)")
            c.commit()
            return cur.rowcount > 0

    def reset(self) -> None:
        with closing(self._conn()) as c:
            c.execute("delete from review"); c.execute("delete from audit"); c.commit()
