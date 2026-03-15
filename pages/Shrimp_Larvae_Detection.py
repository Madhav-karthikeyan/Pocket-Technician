import base64
import importlib.util
import json
import os
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st

DEFAULT_CONF_THRESHOLD = 0.5
MIN_API_CONFIDENCE = 0.1
SCALE_MM_PER_PIXEL = 0.02
FRAME_SKIP = 10
LEARNING_LOG_PATH = Path("data/larvae_learning_log.jsonl")
HIDDEN_MODEL_ID_B64 = "cGwtZGV0ZWN0aW9uLWdrdHllLzM="


def _cv2_available():
    return importlib.util.find_spec("cv2") is not None


#def _get_api_key():
 #   if "ROBOFLOW_API_KEY" in st.secrets:
  #      return st.secrets["ROBOFLOW_API_KEY"]
   # return os.getenv("ROBOFLOW_API_KEY", "kjIdDMpGigBba7txLaog")


#def _get_model_id():
 #   """Return the internal model ID without exposing/editing it in UI controls."""
  #  return base64.b64decode(HIDDEN_MODEL_ID_B64).decode("utf-8")


def _get_model_id():
    """Return the internal model ID without exposing/editing it in UI controls."""
    return base64.b64decode(HIDDEN_MODEL_ID_B64).decode("utf-8")


def classify_stage(length_mm):
    if length_mm < 10:
        return "Post Larvae"
    if length_mm < 30:
        return "Juvenile"
    if length_mm < 60:
        return "Sub-Adult"
    return "Adult"


def stage_color(stage):
    colors = {
        "Post Larvae": (255, 0, 0),
        "Juvenile": (0, 255, 255),
        "Sub-Adult": (0, 165, 255),
        "Adult": (0, 255, 0),
    }
    return colors.get(stage, (255, 255, 255))


def call_roboflow(image, model_id, confidence=MIN_API_CONFIDENCE, overlap=0.35):
    import cv2

    api_key = _get_api_key()
    _, buffer = cv2.imencode(".jpg", image)
    img_base64 = base64.b64encode(buffer).decode("utf-8")

    url = (
        f"https://serverless.roboflow.com/{model_id}"
        f"?api_key={api_key}&confidence={int(confidence * 100)}&overlap={int(overlap * 100)}"
    )
    response = requests.post(
        url,
        data=img_base64,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def _log_learning_event(event):
    LEARNING_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEARNING_LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(event) + "\n")


def analyze_image(image, conf_threshold=DEFAULT_CONF_THRESHOLD, overlap=0.35):
    import cv2

    resolved_model_id = _get_model_id()
    result = call_roboflow(image, model_id=resolved_model_id, confidence=MIN_API_CONFIDENCE, overlap=overlap)
    predictions = result.get("predictions", [])
    filtered_preds = [p for p in predictions if p.get("confidence", 0) >= conf_threshold]

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
        x1, y1 = int(x - w / 2), int(y - h / 2)
        x2, y2 = int(x + w / 2), int(y + h / 2)

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
            "Population Share (%)": round(population_share, 2),
        })

        color = stage_color(stage)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, f"ID:{idx + 1} | {stage}", (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    avg_confidence = np.mean([p["confidence"] for p in filtered_preds]) if filtered_preds else 0
    density = total_count / image_area if image_area > 0 else 0

    stage_distribution = {}
    for shrimp in shrimp_data:
        stage_distribution[shrimp["Stage"]] = stage_distribution.get(shrimp["Stage"], 0) + 1

    summary = {
        "Total Count": total_count,
        "Average Confidence": round(avg_confidence, 3),
        "Average Size (mm)": round(avg_size, 2),
        "Density (pixel-based)": round(density, 6),
        "Stage Distribution": stage_distribution,
    }
    return image, summary, shrimp_data, result


def process_video(video_path, output_path, conf_threshold=DEFAULT_CONF_THRESHOLD, overlap=0.35):
    import cv2

    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    final_summary = None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % FRAME_SKIP == 0:
            annotated_frame, summary, _, _ = analyze_image(
                frame,
                conf_threshold=conf_threshold,
                overlap=overlap,
            )
            final_summary = summary
            out.write(annotated_frame)
        else:
            out.write(frame)

    cap.release()
    out.release()
    return final_summary


def render_shrimp_larvae_detection():
    st.markdown("### 🧠 Shrimp Larvae Detection (CNN)")
    st.caption("Upload larvae image/video to run detection and stage classification.")

    if not _cv2_available():
        st.warning("OpenCV (`cv2`) is not installed in this environment, so larvae detection is unavailable.")
        return

    st.markdown("#### Detection Controls")
    conf_threshold = st.slider(
        "Confidence Threshold (Shown Detections)",
        min_value=0.1,
        max_value=0.9,
        value=DEFAULT_CONF_THRESHOLD,
        step=0.05,
        help="Only detections with confidence greater than or equal to this value are displayed.",
    )
    overlap = st.slider(
        "Crowded Scene Overlap",
        min_value=0.1,
        max_value=0.9,
        value=0.35,
        step=0.05,
        help="Higher overlap helps retain neighboring larvae in dense images.",
    )
    learning_mode = st.toggle(
        "Active Learning Mode",
        value=False,
        help="Save challenging samples + your corrections so you can retrain YOLO and keep improving over time.",
    )

    if learning_mode:
        st.info(
            "Each processed sample can be logged with your corrected count. "
            "Use this log to retrain your YOLO base model periodically."
        )

    uploaded_file = st.file_uploader(
        "Upload Image or Video",
        type=["jpg", "png", "mp4", "avi", "mov"],
        key="larvae_detection_uploader",
    )
    if uploaded_file is None:
        return

    file_type = uploaded_file.name.split(".")[-1].lower()
    try:
        if file_type in ["jpg", "png"]:
            import cv2

            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            with st.spinner("🦐 Analyzing image..."):
                annotated_image, summary, shrimp_data, raw_result = analyze_image(
                    image,
                    conf_threshold=conf_threshold,
                    overlap=overlap,
                )

            st.image(annotated_image, channels="BGR", use_container_width=True)
            st.subheader("📊 Summary")
            for key, value in summary.items():
                st.write(f"**{key}:** {value}")
            st.dataframe(pd.DataFrame(shrimp_data), use_container_width=True)

            if learning_mode:
                corrected_count = st.number_input(
                    "Corrected larvae count (manual truth)",
                    min_value=0,
                    value=int(summary["Total Count"]),
                    step=1,
                    key="corrected_count_image",
                )
                notes = st.text_area("What did the model miss?", key="learning_notes_image")
                if st.button("Save sample for retraining", key="save_learning_image"):
                    timestamp = int(time.time())
                    sample_path = Path("data/active_learning") / f"sample_{timestamp}.jpg"
                    sample_path.parent.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(sample_path), image)
                    _log_learning_event(
                        {
                            "timestamp": timestamp,
                            "sample_path": str(sample_path),
                            "predicted_count": int(summary["Total Count"]),
                            "corrected_count": int(corrected_count),
                            "notes": notes,
                            "predictions": raw_result.get("predictions", []),
                        }
                    )
                    st.success(
                        "Sample logged. Retrain your YOLO base model with these hard examples to improve crowded-scene detection."
                    )

            st.caption(
                "Tip: true online learning is not available directly in hosted inference. "
                "Use the saved learning log as an active-learning dataset, then retrain and deploy a new YOLO version."
            )
            return

        temp_video = tempfile.NamedTemporaryFile(delete=False)
        temp_video.write(uploaded_file.read())
        output_path = f"processed_{int(time.time())}.mp4"
        with st.spinner("Shrimp are being analyzed..."):
            summary = process_video(
                temp_video.name,
                output_path,
                conf_threshold=conf_threshold,
                overlap=overlap,
            )

        st.video(output_path)
        if summary:
            st.subheader("📊 Final Frame Summary")
            for key, value in summary.items():
                st.write(f"**{key}:** {value}")
    except requests.RequestException:
        st.error("Unable to contact the detection API. Please check your API key/network and try again.")
