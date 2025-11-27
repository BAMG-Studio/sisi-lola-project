from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

DB_PATH = Path(os.getenv("AUTH_DB_PATH", Path(__file__).resolve().parents[2] / "data" / "auth.db"))
# Support both ADMIN_SECRET and ADMIN_SECRET_KEY for flexibility
ADMIN_SECRET = os.getenv("ADMIN_SECRET") or os.getenv("ADMIN_SECRET_KEY", "")
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "120"))


def _ensure_dirs() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn():
    _ensure_dirs()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS invites (
                code TEXT PRIMARY KEY,
                email TEXT,
                expires_at INTEGER,
                uses_left INTEGER,
                status TEXT,
                created_at INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS creators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                active INTEGER DEFAULT 1,
                created_at INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                label TEXT,
                created_at INTEGER,
                revoked_at INTEGER,
                FOREIGN KEY (creator_id) REFERENCES creators(id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER,
                api_key_id INTEGER,
                endpoint TEXT,
                status TEXT,
                duration_ms INTEGER,
                result_url TEXT,
                error TEXT,
                created_at INTEGER,
                FOREIGN KEY (creator_id) REFERENCES creators(id),
                FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
            )
            """
        )


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def create_invite(email: str, expires_at: int, uses: int = 1) -> str:
    code = secrets.token_urlsafe(16)
    now = int(time.time())
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO invites (code, email, expires_at, uses_left, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (code, email, expires_at, uses, "active", now),
        )
    return code


def redeem_invite(code: str, email: str, name: Optional[str]) -> Tuple[str, int]:
    now = int(time.time())
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM invites WHERE code = ?", (code,))
        row = cur.fetchone()
        if not row or row["status"] != "active":
            raise ValueError("Invite invalid or used")
        if row["expires_at"] and row["expires_at"] < now:
            raise ValueError("Invite expired")
        if row["uses_left"] <= 0:
            raise ValueError("Invite exhausted")

        cur.execute("INSERT OR IGNORE INTO creators (email, name, active, created_at) VALUES (?, ?, 1, ?)", (email, name, now))
        cur.execute("SELECT id FROM creators WHERE email = ?", (email,))
        creator_id = cur.fetchone()[0]

        api_key_plain = secrets.token_urlsafe(32)
        key_hash = _hash_key(api_key_plain)
        cur.execute(
            "INSERT INTO api_keys (creator_id, key_hash, label, created_at) VALUES (?, ?, ?, ?)",
            (creator_id, key_hash, "default", now),
        )

        uses_left = row["uses_left"] - 1
        status = "used" if uses_left <= 0 else "active"
        cur.execute("UPDATE invites SET uses_left = ?, status = ? WHERE code = ?", (uses_left, status, code))

    return api_key_plain, creator_id


def rotate_key(creator_id: int, label: str = "rotated") -> str:
    now = int(time.time())
    api_key_plain = secrets.token_urlsafe(32)
    key_hash = _hash_key(api_key_plain)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO api_keys (creator_id, key_hash, label, created_at) VALUES (?, ?, ?, ?)",
            (creator_id, key_hash, label, now),
        )
    return api_key_plain


def revoke_key(api_key: str) -> None:
    key_hash = _hash_key(api_key)
    now = int(time.time())
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE api_keys SET revoked_at = ? WHERE key_hash = ?", (now, key_hash))


@dataclass
class AuthContext:
    creator_id: int
    api_key_id: int
    email: str


def validate_api_key(api_key: str) -> AuthContext:
    key_hash = _hash_key(api_key)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT api_keys.id as api_key_id, creators.id as creator_id, creators.email, api_keys.revoked_at
            FROM api_keys
            JOIN creators ON creators.id = api_keys.creator_id
            WHERE api_keys.key_hash = ?
            """,
            (key_hash,),
        )
        row = cur.fetchone()
        if not row or row["revoked_at"]:
            raise ValueError("Invalid or revoked API key")
        return AuthContext(creator_id=row["creator_id"], api_key_id=row["api_key_id"], email=row["email"])


def log_usage(ctx: Optional[AuthContext], endpoint: str, status: str, duration_ms: int = 0, result_url: Optional[str] = None, error: Optional[str] = None) -> None:
    now = int(time.time())
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO usage_logs (creator_id, api_key_id, endpoint, status, duration_ms, result_url, error, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                getattr(ctx, "creator_id", None),
                getattr(ctx, "api_key_id", None),
                endpoint,
                status,
                duration_ms,
                result_url,
                error,
                now,
            ),
        )


def enforce_rate_limit(ctx: AuthContext, endpoint: str) -> None:
    """Simple per-key rolling hour limit."""
    if RATE_LIMIT_PER_HOUR <= 0:
        return
    now = int(time.time())
    window_start = now - 3600
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) FROM usage_logs
            WHERE api_key_id = ? AND created_at >= ?
            """,
            (ctx.api_key_id, window_start),
        )
        count = cur.fetchone()[0]
    if count >= RATE_LIMIT_PER_HOUR:
        raise ValueError(f"Rate limit exceeded ({RATE_LIMIT_PER_HOUR}/hour). Try again later.")


def list_usage(limit: int = 100, creator_id: Optional[int] = None):
    with get_conn() as conn:
        cur = conn.cursor()
        if creator_id:
            cur.execute(
                """
                SELECT * FROM usage_logs WHERE creator_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (creator_id, limit),
            )
        else:
            cur.execute(
                "SELECT * FROM usage_logs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def list_creators():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM creators ORDER BY created_at DESC")
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def list_invites():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM invites ORDER BY created_at DESC")
        rows = cur.fetchall()
    return [dict(r) for r in rows]
