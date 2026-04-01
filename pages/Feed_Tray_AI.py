from datetime import date, datetime
from io import BytesIO

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# Temporary reference chart for 1 lakh stocking.
# This can be replaced with your actual chart later.
REFERENCE_FEED_CHART_100K = [
    {"doc": 1, "abw": 0.03, "feed_kg_day": 1.20, "daily_increment_pct": 8.0},
    {"doc": 5, "abw": 0.08, "feed_kg_day": 1.70, "daily_increment_pct": 7.0},
    {"doc": 10, "abw": 0.20, "feed_kg_day": 2.60, "daily_increment_pct": 6.0},
    {"doc": 15, "abw": 0.40, "feed_kg_day": 3.60, "daily_increment_pct": 5.5},
    {"doc": 20, "abw": 0.70, "feed_kg_day": 5.00, "daily_increment_pct": 5.0},
    {"doc": 25, "abw": 1.10, "feed_kg_day": 6.60, "daily_increment_pct": 4.5},
    {"doc": 30, "abw": 1.70, "feed_kg_day": 8.60, "daily_increment_pct": 4.0},
    {"doc": 40, "abw": 3.20, "feed_kg_day": 11.80, "daily_increment_pct": 3.5},
    {"doc": 50, "abw": 5.20, "feed_kg_day": 14.00, "daily_increment_pct": 3.0},
    {"doc": 60, "abw": 7.80, "feed_kg_day": 15.80, "daily_increment_pct": 2.6},
    {"doc": 70, "abw": 10.80, "feed_kg_day": 17.00, "daily_increment_pct": 2.3},
    {"doc": 80, "abw": 14.20, "feed_kg_day": 18.10, "daily_increment_pct": 2.0},
    {"doc": 90, "abw": 18.00, "feed_kg_day": 18.80, "daily_increment_pct": 1.8},
]


def _reference_row_for_doc(doc):
    row = REFERENCE_FEED_CHART_100K[0]
    for candidate in REFERENCE_FEED_CHART_100K:
        if doc >= candidate["doc"]:
            row = candidate
        else:
            break
    return row


def _tray_adjustment(leftover_pct, daily_increment_pct):
    if leftover_pct <= 5:
        return "Normal Feeding", 1.0
    if leftover_pct >= 10:
        return "Increase Feeding", 1.0 + (daily_increment_pct / 100.0)
    return "Slight Increase", 1.0 + (daily_increment_pct / 200.0)


def _build_projection_from_reference(start_doc, days, start_abw, tray_leftover_pct, stocking_count, survival_pct):
    rows = []
    accumulated = 0.0

    base_start = _reference_row_for_doc(start_doc)
    abw_ratio = (start_abw / base_start["abw"]) if base_start["abw"] > 0 else 1.0
    effective_stocking = max(0.0, float(stocking_count)) * max(0.0, float(survival_pct)) / 100.0
    stocking_factor = effective_stocking / 100000.0 if effective_stocking > 0 else 0.0

    for offset in range(days):
        doc = start_doc + offset
        ref = _reference_row_for_doc(doc)
        base_feed = ref["feed_kg_day"] * abw_ratio
        actual_feed = base_feed * stocking_factor
        daily_increment_pct = ref["daily_increment_pct"]
        tray_action, tray_multiplier = _tray_adjustment(tray_leftover_pct, daily_increment_pct)
        adjusted_feed = actual_feed * tray_multiplier
        accumulated += adjusted_feed

        rows.append(
            {
                "Stocking Count": int(stocking_count),
                "Survival (%)": round(survival_pct, 2),
                "Effective Stocking": int(effective_stocking),
                "DOC": doc,
                "ABW (g)": round(ref["abw"] * abw_ratio, 3),
                "Reference Feed @1 Lakh (kg/day)": round(base_feed, 3),
                "Actual Feed Required (kg/day)": round(actual_feed, 3),
                "Daily Increment (%)": daily_increment_pct,
                "Tray Left (%)": round(tray_leftover_pct, 2),
                "Tray Action": tray_action,
                "Recommended Feed After Tray (kg/day)": round(adjusted_feed, 3),
                "Accumulated Feed (kg)": round(accumulated, 3),
            }
        )

    return pd.DataFrame(rows)


def _build_projection_pdf(df, start_doc):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Feed Tray AI Schedule (Reference Chart - 1 Lakh Stocking)", styles["Title"]),
        Spacer(1, 10),
        Paragraph(f"Start DOC: {start_doc} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]),
        Spacer(1, 10),
    ]

    table_data = [list(df.columns)] + df.values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def render_feed_tray_ai(pond, farm_name, pond_name, feed_tray_logic):
    st.markdown("#### Feed Tray AI")
    st.caption("Dedicated page for check tray logic + DOC-wise feed schedule from reference chart.")

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

    st.subheader("🤖 Feed Projection AI (Reference Chart Based)")
    st.caption(
        "Add stocking details below to calculate actual feed required from the 1 lakh reference chart."
    )

    latest_doc = 1
    if pond["sampling_log"]:
        latest_doc = int(pond["sampling_log"][-1].get("DOC", 1))
    elif pond.get("stocking_date"):
        stocking_doc = datetime.fromisoformat(pond["stocking_date"]).date()
        latest_doc = max(1, (date.today() - stocking_doc).days + 1)

    if pond["sampling_log"]:
        default_abw = float(pond["sampling_log"][-1].get("abw", 0.0))
    else:
        default_abw = float(_reference_row_for_doc(latest_doc)["abw"])

    proj_col1, proj_col2, proj_col3 = st.columns(3)
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
        abw_input = st.number_input(
            "ABW (g) if known",
            min_value=0.0,
            value=round(default_abw, 3),
            step=0.01,
            format="%.3f",
            key="ai_abw_input",
        )

    tray_leftover_pct = st.number_input(
        "Check Tray Leftover (%)",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.5,
        key="ai_tray_leftover_pct",
    )
    stock_col1, stock_col2 = st.columns(2)
    with stock_col1:
        stocking_count = st.number_input(
            "Stocking Count (PL)",
            min_value=0,
            value=int(pond.get("initial_stock", 100000) or 100000),
            step=1000,
            key="ai_stocking_count",
        )
    with stock_col2:
        survival_pct = st.number_input(
            "Expected Survival (%)",
            min_value=0.0,
            max_value=100.0,
            value=85.0,
            step=0.5,
            key="ai_survival_pct",
        )

    projection_df = _build_projection_from_reference(
        start_doc=int(projection_start_doc),
        days=int(projection_days),
        start_abw=float(abw_input) if abw_input > 0 else float(default_abw),
        tray_leftover_pct=float(tray_leftover_pct),
        stocking_count=int(stocking_count),
        survival_pct=float(survival_pct),
    )
    st.dataframe(projection_df, use_container_width=True)

    pdf_bytes = _build_projection_pdf(projection_df, int(projection_start_doc))
    st.download_button(
        "Download Feed Schedule (PDF)",
        data=pdf_bytes,
        file_name=f"feed_schedule_{farm_name}_{pond_name}_doc_{int(projection_start_doc)}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="ai_download_pdf",
    )
