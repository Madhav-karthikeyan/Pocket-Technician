import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "farm_data.db"
JSON_FILE = BASE_DIR / "farm_data.json"
LOCAL_APP_USER_ID = "local::pocket_technician"


def default_payload():
    return {"farms": {}, "memory": {}}


def get_user_id():
    """Return the single local app identity used after removing login/cloud auth."""
    return LOCAL_APP_USER_ID


def _normalize_payload(payload: Optional[dict]):
    safe_payload = payload if isinstance(payload, dict) else default_payload()
    safe_payload.setdefault("farms", {})
    safe_payload.setdefault("memory", {})
    return safe_payload


def _read_legacy_payload(user_id: Optional[str] = None):
    if DB_FILE.exists():
        try:
            with sqlite3.connect(DB_FILE) as conn:
                columns = {
                    row[1] for row in conn.execute("PRAGMA table_info(app_state)").fetchall()
                }
                if "user_id" in columns:
                    row = conn.execute(
                        "SELECT payload FROM app_state WHERE user_id = ?",
                        (user_id or LOCAL_APP_USER_ID,),
                    ).fetchone()
                    if row is None:
                        row = conn.execute(
                            "SELECT payload FROM app_state ORDER BY updated_at DESC LIMIT 1"
                        ).fetchone()
                else:
                    row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()

                if row:
                    return _normalize_payload(json.loads(row[0]))
        except Exception:
            pass

    if JSON_FILE.exists():
        try:
            with JSON_FILE.open("r", encoding="utf-8") as fp:
                payload = json.load(fp)
                if isinstance(payload, dict):
                    users = payload.get("users")
                    if isinstance(users, dict):
                        user_payload = users.get(user_id or LOCAL_APP_USER_ID) or users.get("local_fallback")
                        if isinstance(user_payload, dict):
                            return _normalize_payload(user_payload)
                    return _normalize_payload(payload)
        except Exception:
            pass

    return default_payload()


def _write_legacy_payload(user_id: Optional[str], payload: dict):
    safe_payload = _normalize_payload(payload)
    local_key = user_id or LOCAL_APP_USER_ID

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS app_state ("
                "user_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )
            conn.execute(
                "INSERT INTO app_state (user_id, payload, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET payload = excluded.payload, updated_at = excluded.updated_at",
                (local_key, json.dumps(safe_payload), datetime.utcnow().isoformat()),
            )
            conn.commit()
    except Exception:
        pass

    try:
        with JSON_FILE.open("w", encoding="utf-8") as fp:
            json.dump({"users": {local_key: safe_payload}}, fp, indent=2)
    except Exception:
        pass


def load_user_payload(user_id: str):
    return _read_legacy_payload(user_id or LOCAL_APP_USER_ID)


def save_user_payload(user_id: str, payload: dict):
    _write_legacy_payload(user_id or LOCAL_APP_USER_ID, payload)
