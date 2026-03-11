import cv2
import base64
import requests
import numpy as np
import streamlit as st
import pandas as pd
from datetime import datetime
import tempfile
import time

# =========================
# CONFIGURATION
# =========================

API_KEY = "kjIdDMpGigBba7txLaog"
MODEL_ID = "pl-detection-gktye/3"

CONF_THRESHOLD = 0.5
SCALE_MM_PER_PIXEL = 0.02
FRAME_SKIP = 10  # adjust for API usage control

# =========================
# STAGE CLASSIFICATION
# =========================

def classify_stage(length_mm):
    if length_mm < 10:
        return "Post Larvae"
    elif length_mm < 30:
        return "Juvenile"
    elif length_mm < 60:
        return "Sub-Adult"
    else:
        return "Adult"


def stage_color(stage):
    colors = {
        "Post Larvae": (255, 0, 0),
        "Juvenile": (0, 255, 255),
        "Sub-Adult": (0, 165, 255),
        "Adult": (0, 255, 0)
    }
    return colors.get(stage, (255, 255, 255))


# =========================
# ROBOFLOW API CALL
# =========================

def call_roboflow(image):
    _, buffer = cv2.imencode(".jpg", image)
    img_base64 = base64.b64encode(buffer).decode("utf-8")

    url = f"https://serverless.roboflow.com/{MODEL_ID}?api_key={API_KEY}"

    response = requests.post(
        url,
        data=img_base64,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    return response.json()


# =========================
# IMAGE ANALYSIS FUNCTION
# =========================

def analyze_image(image):

    result = call_roboflow(image)
    predictions = result.get("predictions", [])

    filtered_preds = [
        p for p in predictions
        if p["confidence"] > CONF_THRESHOLD
    ]

    total_count = len(filtered_preds)
    image_height, image_width = image.shape[:2]
    image_area = image_width * image_height

    sizes_mm = []
    shrimp_data = []

    for p in filtered_preds:
        length_px = max(p["width"], p["height"])
        sizes_mm.append(length_px * SCALE_MM_PER_PIXEL)

    avg_size = np.mean(sizes_mm) if sizes_mm else 0

    for idx, p in enumerate(filtered_preds):

        x, y = int(p["x"]), int(p["y"])
        w, h = int(p["width"]), int(p["height"])

        x1, y1 = int(x - w/2), int(y - h/2)
        x2, y2 = int(x + w/2), int(y + h/2)

        length_mm = max(w, h) * SCALE_MM_PER_PIXEL 
        stage = classify_stage(length_mm)

        relative_size = (length_mm / avg_size * 100) if avg_size > 0 else 0
        population_share = (1 / total_count * 100) if total_count > 0 else 0

        shrimp_data.append({
            "Tag ID": idx + 1,
            "Length (mm)": round(length_mm, 2),
            "Stage": stage,
            "Confidence": round(p["confidence"], 3),
            "Relative Size (%)": round(relative_size, 1),
            "Population Share (%)": round(population_share, 2)
        })

        color = stage_color(stage)

        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label = f"ID:{idx+1} | {stage}"
        cv2.putText(image, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)

    avg_confidence = np.mean([p["confidence"] for p in filtered_preds]) if filtered_preds else 0
    density = total_count / image_area if image_area > 0 else 0

    stage_distribution = {}
    for shrimp in shrimp_data:
        stage_distribution[shrimp["Stage"]] = stage_distribution.get(shrimp["Stage"], 0) + 1

    summary = {
        "Total Count": total_count,
        "Average Confidence": round(avg_confidence, 3),
        "Average Size (mm)": round(avg_size, 2) ,
        "Density (pixel-based)": round(density, 6),
        "Stage Distribution": stage_distribution
    }

    return image, summary, shrimp_data


# =========================
# VIDEO PROCESSING
# =========================

def process_video(video_path, output_path):

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    final_summary = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Only call API every FRAME_SKIP frames
        if frame_count % FRAME_SKIP == 0:
            annotated_frame, summary, _ = analyze_image(frame)
            final_summary = summary
            out.write(annotated_frame)
        else:
            # Still write frame, but without API call
            out.write(frame)

    cap.release()
    out.release()
 

    return final_summary

def live_camera_mode():

    st.subheader("📷 Live Camera Detection")

    if "camera_on" not in st.session_state:
        st.session_state.camera_on = False

    col1, col2 = st.columns(2)

    if col1.button("▶ Start Camera"):
        st.session_state.camera_on = True

    if col2.button("⏹ Stop Camera"):
        st.session_state.camera_on = False

    frame_window = st.empty()
    summary_window = st.empty()

    if st.session_state.camera_on:

        cap = cv2.VideoCapture(0)

        frame_count = 0

        while st.session_state.camera_on:

            ret, frame = cap.read()
            if not ret:
                st.error("Camera not accessible.")
                break

            frame_count += 1

            # Only run detection every 20 frames
            if frame_count % 20 == 0:
                annotated_frame, summary, _ = analyze_image(frame)
                frame_window.image(
                    annotated_frame,
                    channels="BGR",
                    use_container_width=True
                )

                with summary_window.container():
                    st.subheader("📊 Live Summary")
                    for key, value in summary.items():
                        st.write(f"**{key}:** {value}")
            else:
                frame_window.image(
                    frame,
                    channels="BGR",
                    use_container_width=True
                )

        cap.release()


# =========================
# STREAMLIT UI
# =========================

st.set_page_config(layout="wide")
st.title("🦐vHatch")

uploaded_file = st.file_uploader("Upload Image or Video", type=["jpg", "png", "mp4", "avi", "mov"])

if uploaded_file is not None:

    file_type = uploaded_file.name.split(".")[-1].lower()

    # IMAGE MODE
    if file_type in ["jpg", "png"]:

        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)

        with st.spinner("🦐 Analyzing image..."):
            annotated_image, summary, shrimp_data = analyze_image(image)

        st.image(annotated_image, channels="BGR", use_container_width=True)

        st.subheader("📊 Summary")
        for key, value in summary.items():
            st.write(f"**{key}:** {value}")

        df = pd.DataFrame(shrimp_data)
        st.dataframe(df, use_container_width=True)

    # VIDEO MODE
    else:

        temp_video = tempfile.NamedTemporaryFile(delete=False)
        temp_video.write(uploaded_file.read())

        output_path = f"processed_{int(time.time())}.mp4"

        spinner_placeholder = st.empty()

        with spinner_placeholder.container():
            st.markdown("## Processing Video... Please Wait")

        with st.spinner("Shrimp are being analyzed..."):
            summary = process_video(temp_video.name, output_path)

        spinner_placeholder.empty()

        st.video(output_path)

        if summary:
            st.subheader("📊 Final Frame Summary")
            for key, value in summary.items():
                st.write(f"**{key}:** {value}")
        
st.divider()
live_camera_mode()
