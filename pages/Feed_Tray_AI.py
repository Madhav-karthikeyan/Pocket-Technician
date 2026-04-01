from datetime import date, datetime

import pandas as pd
import streamlit as st


def build_feed_projection_chart(start_doc, days, base_total_feed, frequency, overrides=None):
    safe_frequency = max(1, int(frequency))
    overrides = overrides or {}

    chart_rows = []
    accumulated_feed = 0.0

    for day_offset in range(days):
        current_doc = start_doc + day_offset
        day_total_feed = float(overrides.get(current_doc, base_total_feed))
        feed_per_schedule = day_total_feed / safe_frequency
        accumulated_feed += day_total_feed

        chart_rows.append(
            {
                "DOC": current_doc,
                "Frequency": safe_frequency,
                "Total Feed (kg/day)": round(day_total_feed, 3),
                "Feed per Schedule (kg)": round(feed_per_schedule, 3),
                "Accumulated Feed (kg)": round(accumulated_feed, 3),
                "Adjusted": "Yes" if current_doc in overrides else "No",
            }
        )

    return pd.DataFrame(chart_rows)


def render_feed_tray_ai(pond, farm_name, pond_name, feed_tray_logic):
    st.markdown("#### Feed Tray AI")
    st.caption("This page is dedicated to feed tray decisions and DOC-wise feed projection.")

    if pond["sampling_log"]:
        last_abw = float(pond["sampling_log"][-1].get("abw", 0.0))
    else:
        last_abw = 0.0
        st.info("No sampling record found yet. Feed tray logic will use ABW = 0.")

    st.subheader("Feed Tray Calculation")
    last_feed = st.number_input("Last Feed Given (kg)", value=10.0, key="ai_last_feed")
    tray_left = st.number_input("Feed Left on Tray (g)", value=5.0, key="ai_tray_left")
    consumed_time = st.number_input("Consumed Time (minutes)", value=60, key="ai_consumed_time")

    if st.button("Calculate Feed Tray Decision", key="ai_calc_feed_tray"):
        result = feed_tray_logic(last_abw, last_feed, tray_left, consumed_time)
        st.json(result)

    st.subheader("🤖 Feed Projection AI")
    st.caption(
        "Project feeding table by DOC using total daily feed and frequency. "
        "Calibrate specific DOC values whenever feed is altered in real operations."
    )

    latest_doc = 1
    if pond["sampling_log"]:
        latest_doc = int(pond["sampling_log"][-1].get("DOC", 1))
    elif pond.get("stocking_date"):
        stocking_doc = datetime.fromisoformat(pond["stocking_date"]).date()
        latest_doc = max(1, (date.today() - stocking_doc).days + 1)

    override_key = f"feed_projection_overrides::{farm_name}::{pond_name}"
    if override_key not in st.session_state:
        st.session_state[override_key] = {}

    proj_col1, proj_col2, proj_col3, proj_col4 = st.columns(4)
    with proj_col1:
        projection_start_doc = st.number_input(
            "Start DOC",
            min_value=1,
            value=latest_doc,
            step=1,
            key="ai_projection_start_doc",
        )
    with proj_col2:
        projection_days = st.number_input(
            "Projection Days",
            min_value=1,
            max_value=180,
            value=14,
            step=1,
            key="ai_projection_days",
        )
    with proj_col3:
        projection_frequency = st.number_input(
            "Feeding Frequency (times/day)",
            min_value=1,
            max_value=12,
            value=4,
            step=1,
            key="ai_projection_frequency",
        )
    with proj_col4:
        projection_total_feed = st.number_input(
            "Total Feed per Day (kg)",
            min_value=0.0,
            value=10.0,
            step=0.1,
            format="%.2f",
            key="ai_projection_total_feed",
        )

    adj_col1, adj_col2, adj_col3 = st.columns([1, 1, 2])
    with adj_col1:
        adjustment_doc = st.number_input(
            "Adjust DOC",
            min_value=1,
            value=projection_start_doc,
            step=1,
            key="ai_adjustment_doc",
        )
    with adj_col2:
        adjusted_feed = st.number_input(
            "Adjusted Total Feed (kg/day)",
            min_value=0.0,
            value=projection_total_feed,
            step=0.1,
            format="%.2f",
            key="ai_adjusted_feed",
        )
    with adj_col3:
        apply_adj_col, remove_adj_col, clear_adj_col = st.columns(3)
        with apply_adj_col:
            if st.button("Apply DOC Adjustment", use_container_width=True, key="ai_apply_adjustment"):
                st.session_state[override_key][int(adjustment_doc)] = float(adjusted_feed)
                st.success(f"Updated DOC {int(adjustment_doc)} to {adjusted_feed:.2f} kg/day.")
        with remove_adj_col:
            if st.button("Remove DOC Adjustment", use_container_width=True, key="ai_remove_adjustment"):
                st.session_state[override_key].pop(int(adjustment_doc), None)
                st.info(f"Removed adjustment for DOC {int(adjustment_doc)}.")
        with clear_adj_col:
            if st.button("Clear All Adjustments", use_container_width=True, key="ai_clear_adjustments"):
                st.session_state[override_key] = {}
                st.info("All DOC adjustments cleared.")

    projection_df = build_feed_projection_chart(
        start_doc=int(projection_start_doc),
        days=int(projection_days),
        base_total_feed=float(projection_total_feed),
        frequency=int(projection_frequency),
        overrides=st.session_state[override_key],
    )
    st.dataframe(projection_df, use_container_width=True)
