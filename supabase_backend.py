import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st
from supabase import Client, create_client

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "farm_data.db"
JSON_FILE = BASE_DIR / "farm_data.json"

APP_STATE_TABLE = "app_state"
SUPABASE_URL= https://hdlkeblroveimxaahcyr.supabase.co 
SUPABASE_ANON_KEY= eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkbGtlYmxyb3ZlaW14YWFoY3lyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUwMTgxOTQsImV4cCI6MjA5MDU5NDE5NH0.YYsNaXNICEpsDutVqtu5qycJU5XDVJGcK9H9orDowjQ


def default_payload():
    return {"farms": {}, "memory": {}}


def _get_supabase_creds():
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", "")).strip()
    anon = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", "")).strip()
    return url, anon


def get_supabase_client() -> Client | None:
    if "supabase_client" in st.session_state:
        return st.session_state["supabase_client"]

    url, anon = _get_supabase_creds()
    if not url or not anon:
        return None

    client = create_client(url, anon)
    st.session_state["supabase_client"] = client
    return client


def ensure_auth_state():
    st.session_state.setdefault("auth_user", None)


def get_user_id():
    user = st.session_state.get("auth_user")
    if not user:
        return None
    return user.get("id")


def render_auth_ui() -> bool:
    ensure_auth_state()
    client = get_supabase_client()

    if client is None:
        st.error("Supabase is not configured. Add SUPABASE_URL and SUPABASE_ANON_KEY to Streamlit secrets.")
        return False

    user = st.session_state.get("auth_user")
    if user:
        with st.sidebar:
            st.success(f"Logged in as: {user.get('email', 'Unknown')}")
            if st.button("Logout", use_container_width=True):
                client.auth.sign_out()
                st.session_state["auth_user"] = None
                st.rerun()
        return True

    st.title("Pocket Technician Login")
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn", use_container_width=True):
            try:
                response = client.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["auth_user"] = response.user.model_dump()
                st.success("Login successful")
                st.rerun()
            except Exception as exc:
                st.error(f"Login failed: {exc}")

    with signup_tab:
        email = st.text_input("New Email", key="signup_email")
        password = st.text_input("New Password", type="password", key="signup_password")
        if st.button("Create Account", key="signup_btn", use_container_width=True):
            try:
                client.auth.sign_up({"email": email, "password": password})
                st.success("Signup successful. Verify email if confirmation is enabled, then log in.")
            except Exception as exc:
                st.error(f"Signup failed: {exc}")

    return False


def _read_legacy_payload():
    if DB_FILE.exists():
        try:
            with sqlite3.connect(DB_FILE) as conn:
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
                    payload.setdefault("farms", {})
                    payload.setdefault("memory", {})
                    return payload
        except Exception:
            pass

    return default_payload()


def load_user_payload(user_id: str):
    client = get_supabase_client()
    if client is None or not user_id:
        return default_payload()

    try:
        response = (
            client.table(APP_STATE_TABLE)
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

        legacy = _read_legacy_payload()
        save_user_payload(user_id, legacy)
        return legacy
    except Exception as exc:
        st.error(f"Failed loading Supabase data: {exc}")
        return default_payload()


def save_user_payload(user_id: str, payload: dict):
    client = get_supabase_client()
    if client is None or not user_id:
        return

    safe_payload = payload if isinstance(payload, dict) else default_payload()
    safe_payload.setdefault("farms", {})
    safe_payload.setdefault("memory", {})

    try:
        client.table(APP_STATE_TABLE).upsert(
            {
                "user_id": user_id,
                "payload": safe_payload,
                "updated_at": datetime.utcnow().isoformat(),
            },
            on_conflict="user_id",
        ).execute()
    except Exception as exc:
        st.error(f"Failed saving Supabase data: {exc}")
