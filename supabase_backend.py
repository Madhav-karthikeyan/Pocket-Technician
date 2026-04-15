import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st
from typing import Any, Optional

try:
    from supabase import Client, create_client
except Exception:  # supabase package may be unavailable in some deployments
    Client = Any  # type: ignore
    create_client = None

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "farm_data.db"
JSON_FILE = BASE_DIR / "farm_data.json"
USER_LOG_FILE = BASE_DIR / "user_log.json"

MISSING_TABLE_FLAG = "supabase_missing_table_warned"


def default_payload():
    return {"farms": {}, "memory": {}}


def get_app_state_table() -> str:
    configured = st.secrets.get("SUPABASE_APP_STATE_TABLE", os.getenv("SUPABASE_APP_STATE_TABLE", "")).strip()
    return configured or "app_state"


def _is_missing_table_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "pgrst205" in text or "could not find the table" in text


def _show_missing_table_help(table_name: str):
    if st.session_state.get(MISSING_TABLE_FLAG):
        return
    st.session_state[MISSING_TABLE_FLAG] = True
    # Keep this silent in the UI and gracefully fall back to local storage paths.
    # A console warning preserves debuggability without interrupting users.
    print(
        f"[Supabase] Missing table public.{table_name} (or not exposed to API). "
        "Using local fallback state."
    )


def _get_supabase_creds():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", "")).strip()
    anon = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", "")).strip()
    return url, anon


def get_supabase_client() -> Optional[Client]:
    if "supabase_client" in st.session_state:
        return st.session_state["supabase_client"]

    if create_client is None:
        return None

    url, anon = _get_supabase_creds()
    if not url or not anon:
        return None

    client = create_client(url, anon)
    st.session_state["supabase_client"] = client
    return client


def ensure_auth_state():
    st.session_state.setdefault("auth_user", None)


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _local_user_id(email: str) -> str:
    return f"local::{_normalize_email(email)}"


def _is_network_error(exc: Exception) -> bool:
    text = str(exc).lower()
    keywords = [
        "name or service not known",
        "temporary failure in name resolution",
        "failed to establish a new connection",
        "connection refused",
        "connection reset",
        "network is unreachable",
        "timed out",
    ]
    return any(word in text for word in keywords)


def _read_user_log() -> dict:
    if USER_LOG_FILE.exists():
        try:
            with USER_LOG_FILE.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
                if isinstance(data, dict):
                    users = data.get("users")
                    if isinstance(users, list):
                        return {"users": users}
        except Exception:
            pass
    return {"users": []}


def _write_user_log(data: dict):
    safe_data = data if isinstance(data, dict) else {"users": []}
    users = safe_data.get("users")
    if not isinstance(users, list):
        safe_data["users"] = []
    with USER_LOG_FILE.open("w", encoding="utf-8") as fp:
        json.dump(safe_data, fp, indent=2)


def _local_sign_in(email: str, password: str) -> Optional[dict]:
    target_email = _normalize_email(email)
    raw_password = (password or "").strip()
    if not target_email or not raw_password:
        return None

    for user in _read_user_log()["users"]:
        if (
            isinstance(user, dict)
            and _normalize_email(user.get("email", "")) == target_email
            and user.get("password") == raw_password
        ):
            return {
                "id": _local_user_id(target_email),
                "email": target_email,
                "provider": "local",
            }
    return None


def _local_sign_up(email: str, password: str) -> tuple[bool, str]:
    target_email = _normalize_email(email)
    raw_password = (password or "").strip()
    if not target_email or not raw_password:
        return False, "Email and password are required."

    data = _read_user_log()
    for user in data["users"]:
        if isinstance(user, dict) and _normalize_email(user.get("email", "")) == target_email:
            return False, "An account with this email already exists."

    data["users"].append({"email": target_email, "password": raw_password})
    _write_user_log(data)
    return True, "Local account created successfully."


def get_user_id():
    user = st.session_state.get("auth_user")
    if not user:
        return None
    return user.get("id")


def render_auth_ui() -> bool:
    ensure_auth_state()
    client = get_supabase_client()
    supabase_enabled = client is not None

    user = st.session_state.get("auth_user")
    if user:
        with st.sidebar:
            st.success(f"Logged in as: {user.get('email', 'Unknown')}")
            if st.button("Logout", use_container_width=True):
                if client is not None:
                    client.auth.sign_out()
                st.session_state["auth_user"] = None
                st.rerun()
        return True

    st.title("Pocket Technician Login")
    if create_client is None:
        st.warning("Supabase SDK is unavailable. Local login mode is enabled.")
    elif not supabase_enabled:
        st.warning("Supabase is not configured. Local login mode is enabled.")

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn", use_container_width=True):
            if supabase_enabled:
                try:
                    response = client.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state["auth_user"] = response.user.model_dump()
                    st.success("Login successful")
                    st.rerun()
                except Exception as exc:
                    if _is_network_error(exc):
                        local_user = _local_sign_in(email, password)
                        if local_user:
                            st.session_state["auth_user"] = local_user
                            st.warning("Supabase is unreachable. Logged in with local offline account.")
                            st.rerun()
                        st.error("Login failed in offline mode. Check your email/password or create a local account in Sign Up.")
                    else:
                        st.error(f"Login failed: {exc}")
            else:
                local_user = _local_sign_in(email, password)
                if local_user:
                    st.session_state["auth_user"] = local_user
                    st.success("Login successful (local mode)")
                    st.rerun()
                else:
                    st.error("Login failed in local mode. Please check your credentials or create an account.")

    with signup_tab:
        email = st.text_input("New Email", key="signup_email")
        password = st.text_input("New Password", type="password", key="signup_password")
        if st.button("Create Account", key="signup_btn", use_container_width=True):
            if supabase_enabled:
                try:
                    client.auth.sign_up({"email": email, "password": password})
                    st.success("Signup successful. Verify email if confirmation is enabled, then log in.")
                except Exception as exc:
                    if _is_network_error(exc):
                        ok, message = _local_sign_up(email, password)
                        if ok:
                            st.warning("Supabase is unreachable. Created local offline account instead.")
                        else:
                            st.error(message)
                    else:
                        st.error(f"Signup failed: {exc}")
            else:
                ok, message = _local_sign_up(email, password)
                if ok:
                    st.success("Signup successful (local mode).")
                else:
                    st.error(message)

    return False


def _read_legacy_payload(user_id: Optional[str] = None):
    if DB_FILE.exists():
        try:
            with sqlite3.connect(DB_FILE) as conn:
                columns = {
                    row[1] for row in conn.execute("PRAGMA table_info(app_state)").fetchall()
                }
                if "user_id" in columns:
                    if user_id:
                        row = conn.execute(
                            "SELECT payload FROM app_state WHERE user_id = ?",
                            (user_id,),
                        ).fetchone()
                    else:
                        row = conn.execute(
                            "SELECT payload FROM app_state ORDER BY updated_at DESC LIMIT 1"
                        ).fetchone()
                else:
                    row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()

                if row:
                    payload = json.loads(row[0])
                    if isinstance(payload, dict):
                        payload.setdefault("farms", {})
                        payload.setdefault("memory", {})
                        return payload
        except Exception:
            pass

    if JSON_FILE.exists():
        try:
            with JSON_FILE.open("r", encoding="utf-8") as fp:
                payload = json.load(fp)
                if isinstance(payload, dict):
                    if user_id and isinstance(payload.get("users"), dict):
                        user_payload = payload["users"].get(user_id)
                        if isinstance(user_payload, dict):
                            user_payload.setdefault("farms", {})
                            user_payload.setdefault("memory", {})
                            return user_payload
                        return default_payload()
                    payload.setdefault("farms", {})
                    payload.setdefault("memory", {})
                    return payload
        except Exception:
            pass

    return default_payload()


def _write_legacy_payload(user_id: Optional[str], payload: dict):
    safe_payload = payload if isinstance(payload, dict) else default_payload()
    safe_payload.setdefault("farms", {})
    safe_payload.setdefault("memory", {})

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS app_state ("
                "user_id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at TEXT NOT NULL)"
            )
            key = user_id or "local_fallback"
            conn.execute(
                "INSERT INTO app_state (user_id, payload, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET payload = excluded.payload, updated_at = excluded.updated_at",
                (key, json.dumps(safe_payload), datetime.utcnow().isoformat()),
            )
            conn.commit()
    except Exception:
        pass

    try:
        existing = {}
        if JSON_FILE.exists():
            with JSON_FILE.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)
                if isinstance(raw, dict):
                    existing = raw

        users = existing.get("users") if isinstance(existing.get("users"), dict) else {}
        users[user_id or "local_fallback"] = safe_payload
        with JSON_FILE.open("w", encoding="utf-8") as fp:
            json.dump({"users": users}, fp)
    except Exception:
        pass


def load_user_payload(user_id: str):
    client = get_supabase_client()
    if not user_id:
        return default_payload()
    if client is None:
        return _read_legacy_payload(user_id)

    try:
        response = (
            client.table(get_app_state_table())
            .select("payload")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if response.data:
            payload = response.data[0].get("payload") or {}
            if isinstance(payload, dict):
                payload.setdefault("farms", {})
                payload.setdefault("memory", {})
                return payload

        legacy = _read_legacy_payload(user_id)
        save_user_payload(user_id, legacy)
        return legacy
    except Exception as exc:
        if _is_missing_table_error(exc):
            _show_missing_table_help(get_app_state_table())
            return _read_legacy_payload(user_id)
        st.error(f"Failed loading Supabase data: {exc}")
        return default_payload()


def save_user_payload(user_id: str, payload: dict):
    client = get_supabase_client()
    if not user_id:
        return
    if client is None:
        _write_legacy_payload(user_id, payload)
        return

    safe_payload = payload if isinstance(payload, dict) else default_payload()
    safe_payload.setdefault("farms", {})
    safe_payload.setdefault("memory", {})

    try:
        client.table(get_app_state_table()).upsert(
            {
                "user_id": user_id,
                "payload": safe_payload,
                "updated_at": datetime.utcnow().isoformat(),
            },
            on_conflict="user_id",
        ).execute()
    except Exception as exc:
        if _is_missing_table_error(exc):
            _show_missing_table_help(get_app_state_table())
            _write_legacy_payload(user_id, safe_payload)
            return
        st.error(f"Failed saving Supabase data: {exc}")
