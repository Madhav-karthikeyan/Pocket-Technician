import json
import os
import sqlite3
from datetime import date, datetime

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "farm_data.db")
DATA_FILE = os.path.join(BASE_DIR, "farm_data.json")


def _default_data():
    return {"farms": {}}


def _load_data():
    if os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
            if row:
                loaded = json.loads(row[0])
                if isinstance(loaded, dict):
                    loaded.setdefault("farms", {})
                    return loaded

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                loaded.setdefault("farms", {})
                return loaded

    return _default_data()


def _calc_doc(stocking_date_str: str):
    try:
        return (date.today() - datetime.fromisoformat(stocking_date_str).date()).days + 1
    except Exception:
        return 1


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _simulate_deb(config: dict, scenario: dict) -> pd.DataFrame:
    horizon = int(scenario["horizon_days"])
    doc_start = int(config["doc"])

    current_biomass = float(config["current_biomass_kg"])
    total_feed_used = float(config["accum_feed_kg"])
    survival_pct = float(config["survival_pct"])

    feed_cost_per_kg = 45 * (1 + scenario["feed_cost_adj"] / 100)
    sale_price_per_kg = 260 * (1 + scenario["sale_price_adj"] / 100)

    assim_eff = 0.68
    k_maint = 0.0065
    daily_mortality = max(0.0, 0.0015 * (1 - scenario["survival_adj"] / 100))

    records = []

    for day in range(horizon + 1):
        doc = doc_start + day

        if doc < 30:
            ration_pct = 0.06
        elif doc < 60:
            ration_pct = 0.045
        elif doc < 90:
            ration_pct = 0.035
        else:
            ration_pct = 0.028

        daily_feed = max(0.0, current_biomass * ration_pct)
        assimilation_gain = daily_feed * assim_eff
        maintenance_loss = current_biomass * k_maint
        net_growth = max(-current_biomass * 0.03, assimilation_gain - maintenance_loss)

        if day > 0:
            survival_pct = max(0.0, survival_pct * (1 - daily_mortality))
            survival_factor = max(0.0, survival_pct / 100)
            current_biomass = max(0.0, current_biomass + net_growth * survival_factor)
            total_feed_used += daily_feed

        revenue = current_biomass * sale_price_per_kg
        feed_cost = total_feed_used * feed_cost_per_kg
        profit = revenue - feed_cost

        records.append(
            {
                "Pond": config["pond_name"],
                "DOC": doc,
                "Biomass (kg)": current_biomass,
                "Daily Feed (kg)": daily_feed,
                "Accumulated Feed (kg)": total_feed_used,
                "Survival (%)": survival_pct,
                "Revenue (₹)": revenue,
                "Feed Cost (₹)": feed_cost,
                "Profit (₹)": profit,
            }
        )

    return pd.DataFrame(records)


def render_virtual_farm(standalone: bool = True):
    if standalone:
        st.set_page_config("Virtual Farm", layout="wide")

    st.title("🌐 Virtual Farm")
    st.caption("Project culture growth with a simple DEB-style simulation using what-if controls.")

    data = _load_data()
    farm_names = sorted(data.get("farms", {}).keys())

    if not farm_names:
        st.warning("No farms available yet. Please enter farm and pond data from the main page first.")
        return

    farm_name = st.selectbox("Farm", farm_names)
    farm = data["farms"][farm_name]
    ponds = farm.get("ponds", {})

    if not ponds:
        st.warning("No ponds available in this farm.")
        return

    st.subheader("Initial Inputs")
    st.caption("You can keep decimal/fraction values for pond dimensions and tune pond-level simulation assumptions.")

    input_rows = []
    for pond_name, pond in sorted(ponds.items()):
        latest = {}
        sampling_log = pond.get("sampling_log", [])
        if sampling_log:
            latest = sampling_log[-1]

        area = _safe_float(pond.get("area", 0.0))
        depth = _safe_float(pond.get("depth", 0.0))
        volume = area * depth
        initial_stock = _safe_float(pond.get("initial_stock", 0.0))
        stocking_density = (initial_stock / area) if area > 0 else 0.0
        stocking_date = pond.get("stocking_date", str(date.today()))
        doc = _calc_doc(stocking_date)

        current_biomass = _safe_float(latest.get("biomass", 0.0))
        if current_biomass <= 0:
            current_biomass = initial_stock * 0.002

        total_feed = sum(_safe_float(item.get("feed", 0.0)) for item in pond.get("feed_log", []))
        survival = _safe_float(latest.get("survival_pct", latest.get("survival", 80.0)), 80.0)

        input_rows.append(
            {
                "Pond": pond_name,
                "Pond Area (m²)": round(area, 2),
                "Avg Depth (m)": round(depth, 2),
                "Pond Volume (m³)": round(volume, 2),
                "Stocking Density (#/m²)": round(stocking_density, 2),
                "Stocking Date": stocking_date,
                "Current DOC": doc,
                "Current Biomass (kg)": round(current_biomass, 2),
                "Accumulated Feed (kg)": round(total_feed, 2),
                "Current Survival (%)": round(survival, 2),
            }
        )

    input_df = pd.DataFrame(input_rows)
    st.dataframe(input_df, use_container_width=True)

    st.subheader("What-if Scenario Controls")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        horizon_days = st.number_input("Projection Horizon (days)", min_value=7, max_value=240, value=45, step=1)
    with c2:
        survival_adj = st.slider("Survival Improvement (%)", min_value=-20, max_value=30, value=0)
    with c3:
        feed_cost_adj = st.slider("Feed Cost Change (%)", min_value=-30, max_value=40, value=0)
    with c4:
        sale_price_adj = st.slider("Sale Price Change (%)", min_value=-30, max_value=40, value=0)

    if st.button("🚀 Project", type="primary", key="vf_project"):
        scenario = {
            "horizon_days": horizon_days,
            "survival_adj": survival_adj,
            "feed_cost_adj": feed_cost_adj,
            "sale_price_adj": sale_price_adj,
        }

        all_runs = []
        for row in input_rows:
            config = {
                "pond_name": row["Pond"],
                "doc": row["Current DOC"],
                "current_biomass_kg": row["Current Biomass (kg)"],
                "accum_feed_kg": row["Accumulated Feed (kg)"],
                "survival_pct": row["Current Survival (%)"],
            }
            all_runs.append(_simulate_deb(config, scenario))

        st.session_state["virtual_projection_df"] = pd.concat(all_runs, ignore_index=True)

    if "virtual_projection_df" not in st.session_state:
        st.info("Set your what-if controls and click **Project** to run DEB-style projection.")
        return

    projection_df = st.session_state["virtual_projection_df"]
    last_doc = projection_df.groupby("Pond", as_index=False).tail(1).copy()

    st.subheader("Projected Farm Summary")
    summary = pd.DataFrame(
        {
            "Total Projected Biomass (kg)": [last_doc["Biomass (kg)"].sum()],
            "Total Feed Accumulated (kg)": [last_doc["Accumulated Feed (kg)"].sum()],
            "Total Projected Revenue (₹)": [last_doc["Revenue (₹)"].sum()],
            "Total Projected Feed Cost (₹)": [last_doc["Feed Cost (₹)"].sum()],
            "Total Projected Profit (₹)": [last_doc["Profit (₹)"].sum()],
        }
    )
    st.dataframe(summary.round(2), use_container_width=True)

    st.subheader("Essential Projection Graphs (Line Charts)")

    fig1, ax1 = plt.subplots()
    for pond_name, pond_df in projection_df.groupby("Pond"):
        ax1.plot(pond_df["DOC"], pond_df["Biomass (kg)"], marker=".", label=pond_name)
    ax1.set_title("Biomass Projection by DOC")
    ax1.set_xlabel("DOC")
    ax1.set_ylabel("Biomass (kg)")
    ax1.legend()
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    for pond_name, pond_df in projection_df.groupby("Pond"):
        ax2.plot(pond_df["DOC"], pond_df["Accumulated Feed (kg)"], marker=".", label=pond_name)
    ax2.set_title("Total Feed Accumulation by DOC")
    ax2.set_xlabel("DOC")
    ax2.set_ylabel("Feed (kg)")
    ax2.legend()
    st.pyplot(fig2)

    fig3, ax3 = plt.subplots()
    for pond_name, pond_df in projection_df.groupby("Pond"):
        ax3.plot(pond_df["DOC"], pond_df["Profit (₹)"], marker=".", label=pond_name)
    ax3.axhline(0, color="black", linewidth=1)
    ax3.set_title("Profitability Projection by DOC")
    ax3.set_xlabel("DOC")
    ax3.set_ylabel("Profit (₹)")
    ax3.legend()
    st.pyplot(fig3)

    st.success("Projection complete. Adjust controls and click Project again to run another what-if scenario.")


if __name__ == "__main__":
    render_virtual_farm(standalone=True)
