import os
import cv2
import json
import math
import uuid
import zipfile
import random
import shutil
import tempfile
import threading
import time
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
from collections import deque
from ultralytics import YOLO

# ================= Optional dependencies =================
try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    HAS_DEEPSORT = True
except Exception:
    HAS_DEEPSORT = False

try:
    from deepface import DeepFace
    HAS_DEEPFACE = True
except Exception:
    HAS_DEEPFACE = False

try:
    import av
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoProcessorBase
    HAS_WEBRTC = True
except Exception:
    HAS_WEBRTC = False

# ================= App config =================
st.set_page_config(page_title="Smart Shop Analytics", layout="wide")
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.2rem; padding-bottom: 1.2rem;}
      .title {font-size: 2rem; font-weight: 700;}
      .sub {color:#666; margin-bottom: 1rem;}
    </style>
    <div class="title">Smart Shop Analytics</div>
    <div class="sub">Step 1: Train from dataset → Step 2: Track Video / Theft Video / Live Webcam</div>
    """,
    unsafe_allow_html=True
)

OUT_DIR = Path("smartshop_outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = OUT_DIR / "app_state.json"

CONF_THRES = 0.45
IOU_THRES = 0.50
AGE_GENDER_EVERY_N_FRAMES = 20
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
WEBCAM_CONF_THRES = 0.25
WEBCAM_MAX_WIDTH = 480
WEBCAM_INFER_INTERVAL_SEC = 0.45  # ~2.2 inference/sec on CPU for smooth stream
LOCAL_WEBCAM_SECONDS_DEFAULT = 45
LOCAL_WEBCAM_FPS = 20
LOCAL_WEBCAM_INFER_EVERY = 2

THEFT_CONFIG = {
    "loiter_seconds": 12,
    "zone_var_threshold": 180,      # low movement variance
    "direction_changes_threshold": 5,
    "quick_exit_seconds": 6,
    "high_speed_px_per_sec": 320,
}
RISK_WEIGHTS = {
    "LOITERING": 30,
    "ERRATIC_MOVEMENT": 20,
    "QUICK_EXIT": 35,
    "HIGH_SPEED_NEAR_EXIT": 25,
}

if HAS_WEBRTC:
    RTC_CFG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

# ================= Session state =================
if "training_done" not in st.session_state:
    st.session_state.training_done = False
if "cls_model_path" not in st.session_state:
    st.session_state.cls_model_path = None
if "detect_model_path" not in st.session_state:
    st.session_state.detect_model_path = "yolov8n.pt"

if STATE_FILE.exists():
    try:
        persisted = json.loads(STATE_FILE.read_text())
        st.session_state.training_done = bool(persisted.get("training_done", st.session_state.training_done))
        st.session_state.cls_model_path = persisted.get("cls_model_path", st.session_state.cls_model_path)
    except Exception:
        pass

# ================= Cached resources =================
@st.cache_resource
def load_detect_model(path: str):
    return YOLO(path)

@st.cache_resource
def load_face_cascade():
    return cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def get_detect_model():
    model_path = st.session_state.get("detect_model_path", "yolov8n.pt")
    return load_detect_model(model_path)

face_cascade = load_face_cascade()

def make_tracker(live=False):
    if not HAS_DEEPSORT:
        raise RuntimeError("deep-sort-realtime not installed.")
    try:
        # live webcam on CPU is much faster with IoU-only tracking
        if live:
            return DeepSort(max_age=30, n_init=2, max_iou_distance=0.7, nn_budget=100, embedder=None)
        return DeepSort(max_age=30, n_init=3, max_iou_distance=0.7, nn_budget=100, embedder="mobilenet")
    except Exception:
        # fallback without appearance embedder
        return DeepSort(max_age=30, n_init=3, max_iou_distance=0.7, nn_budget=100, embedder=None)

# ================= Utility functions =================
def age_to_group(age: int) -> str:
    if age <= 12: return "0-12"
    if age <= 19: return "13-19"
    if age <= 29: return "20-29"
    if age <= 39: return "30-39"
    if age <= 49: return "40-49"
    if age <= 59: return "50-59"
    return "60+"

def fallback_age_range(bbox_h: int, frame_h: int) -> str:
    # Conservative fallback if face/DeepFace unavailable
    r = bbox_h / max(frame_h, 1)
    if r >= 0.65:
        return "20-40"
    if r >= 0.45:
        return "20-50"
    return "15-60"

def detect_largest_face(person_roi):
    if person_roi is None or person_roi.size == 0:
        return None
    gray = cv2.cvtColor(person_roi, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return person_roi[y:y+h, x:x+w]

def estimate_age_gender(person_roi, bbox_h=None, frame_h=None):
    # Returns (age_range, gender)
    if HAS_DEEPFACE:
        try:
            # try face crop first
            face = detect_largest_face(person_roi)
            target = face if face is not None and face.size > 0 else person_roi
            if target is not None and target.size > 0:
                result = DeepFace.analyze(
                    img_path=target,
                    actions=["age", "gender"],
                    enforce_detection=False,
                    detector_backend="opencv",
                    silent=True
                )
                if isinstance(result, list):
                    result = result[0]
                age = result.get("age", None)
                gender = result.get("dominant_gender", None)
                if age is not None:
                    ag = age_to_group(int(round(age)))
                else:
                    ag = fallback_age_range(bbox_h or 0, frame_h or 1)
                if gender is None:
                    gender = "Unknown"
                return ag, gender
        except Exception:
            pass

    # fallback
    ag = fallback_age_range(bbox_h or 0, frame_h or 1)
    return ag, "Unknown"

def fmt_duration(sec):
    sec = int(max(0, sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

def is_near_exit(x1, y1, x2, y2, w, h):
    return (x2 > int(0.88 * w)) or (x1 < int(0.12 * w)) or (y2 > int(0.82 * h))

def risk_color(score):
    if score <= 30: return (0, 255, 0)
    if score <= 60: return (0, 255, 255)
    if score <= 80: return (0, 165, 255)
    return (0, 0, 255)

def init_track(track_data, tid, frame_idx, fps):
    if tid not in track_data:
        track_data[tid] = {
            "start_frame": frame_idx,
            "end_frame": frame_idx,
            "pos": deque(maxlen=max(60, int(fps * 12))),
            "age": None,
            "gender": None,
            "last_ag_frame": -999,
            "ag_votes": deque(maxlen=5),
            "trail": deque(maxlen=60),
            "risk_max": 0,
            "reasons": set(),
        }

def make_people_df(track_data, fps):
    rows = []
    for tid, td in track_data.items():
        entry = td["start_frame"] / fps if fps > 0 else 0
        exit_ = td["end_frame"] / fps if fps > 0 else 0
        duration = max(0, exit_ - entry)
        rows.append({
            "Person_ID": tid,
            "Entry_sec": round(entry, 2),
            "Exit_sec": round(exit_, 2),
            "Duration_sec": round(duration, 2),
            "Gender": td["gender"],
            "Age_Range": td["age"],
            "Max_Risk": td["risk_max"],
            "Reasons": ",".join(sorted(td["reasons"])) if td["reasons"] else ""
        })
    cols = ["Person_ID", "Entry_sec", "Exit_sec", "Duration_sec", "Gender", "Age_Range", "Max_Risk", "Reasons"]
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows)[cols].sort_values("Duration_sec", ascending=False).reset_index(drop=True)

# ================= Training (classification ZIP) =================
def choose_train_config(total_images: int):
    if total_images < 1500:
        return {"epochs": 20, "imgsz": 224, "batch": 32, "patience": 8}
    elif total_images < 5000:
        return {"epochs": 30, "imgsz": 224, "batch": 48, "patience": 10}
    else:
        return {"epochs": 40, "imgsz": 224, "batch": 64, "patience": 12}

def find_candidate_root_with_classes(extract_root: Path):
    for root, dirs, _ in os.walk(extract_root):
        root_p = Path(root)
        class_dirs = []
        for d in dirs:
            p = root_p / d
            if p.is_dir():
                has_img = any(x.suffix.lower() in IMG_EXTS for x in p.rglob("*"))
                if has_img:
                    class_dirs.append(p)
        if len(class_dirs) >= 2:
            return root_p, class_dirs
    return None, []

def prepare_cls_data(zip_file, split_ratio=0.8, seed=42):
    temp_dir = Path(tempfile.mkdtemp(prefix="cls_data_"))
    zip_path = temp_dir / "dataset.zip"
    zip_file.seek(0)
    with open(zip_path, "wb") as f:
        f.write(zip_file.read())

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(temp_dir)

    _, class_dirs = find_candidate_root_with_classes(temp_dir)
    if len(class_dirs) < 2:
        raise RuntimeError("Could not find at least two class folders with images in ZIP.")

    out_root = temp_dir / "prepared_cls"
    train_root = out_root / "train"
    val_root = out_root / "val"
    train_root.mkdir(parents=True, exist_ok=True)
    val_root.mkdir(parents=True, exist_ok=True)

    random.seed(seed)
    stats = {}

    for class_dir in sorted(class_dirs, key=lambda p: p.name):
        cls = class_dir.name
        imgs = [p for p in class_dir.rglob("*") if p.suffix.lower() in IMG_EXTS]
        if not imgs:
            continue

        random.shuffle(imgs)
        n_train = max(1, int(len(imgs) * split_ratio))
        train_imgs = imgs[:n_train]
        val_imgs = imgs[n_train:] if (len(imgs) - n_train) > 0 else imgs[-1:]

        (train_root / cls).mkdir(parents=True, exist_ok=True)
        (val_root / cls).mkdir(parents=True, exist_ok=True)

        for src in train_imgs:
            dst = train_root / cls / src.name
            if dst.exists():
                dst = train_root / cls / f"{uuid.uuid4().hex[:8]}_{src.name}"
            shutil.copy2(src, dst)

        for src in val_imgs:
            dst = val_root / cls / src.name
            if dst.exists():
                dst = val_root / cls / f"{uuid.uuid4().hex[:8]}_{src.name}"
            shutil.copy2(src, dst)

        stats[cls] = {"total": len(imgs), "train": len(train_imgs), "val": len(val_imgs)}

    return out_root, stats

def train_cls_from_zip_auto(zip_file, base_model="yolov8n-cls.pt", split_ratio=0.8):
    data_root, stats = prepare_cls_data(zip_file, split_ratio=split_ratio)
    total_images = sum(v["total"] for v in stats.values())
    cfg = choose_train_config(total_images)

    cls_model = YOLO(base_model)
    run_name = f"cls_{uuid.uuid4().hex[:8]}"
    cls_model.train(
        data=str(data_root),
        epochs=cfg["epochs"],
        imgsz=cfg["imgsz"],
        batch=cfg["batch"],
        patience=cfg["patience"],
        project=str(OUT_DIR / "runs_cls"),
        name=run_name,
        pretrained=True,
        verbose=True
    )

    best_path = str(cls_model.trainer.best) if getattr(cls_model.trainer, "best", None) else ""
    save_dir = Path(cls_model.trainer.save_dir)
    results_csv = save_dir / "results.csv"

    top1, top5 = None, None
    if results_csv.exists():
        df = pd.read_csv(results_csv)
        top1_cols = [c for c in df.columns if "top1" in c.lower()]
        top5_cols = [c for c in df.columns if "top5" in c.lower()]
        if top1_cols:
            top1 = float(df[top1_cols[0]].dropna().iloc[-1])
        if top5_cols:
            top5 = float(df[top5_cols[0]].dropna().iloc[-1])

    return {
        "best_path": best_path,
        "save_dir": str(save_dir),
        "results_csv": str(results_csv) if results_csv.exists() else None,
        "class_stats": stats,
        "top1": top1,
        "top5": top5,
        "total_images": total_images,
        "used_config": cfg
    }

# ================= Core frame processing =================
def process_frame(frame, model, tracker, track_data, frame_idx, fps, theft_mode, heatmap=None, event_log=None, conf_thres=CONF_THRES, enable_age_gender=True):
    h, w = frame.shape[:2]
    t_sec = frame_idx / fps if fps > 0 else 0.0

    # detect person only
    results = model.predict(frame, conf=conf_thres, iou=IOU_THRES, classes=[0], verbose=False)
    detections = []
    if len(results[0].boxes) > 0:
        for b, c in zip(results[0].boxes.xyxy, results[0].boxes.conf):
            x1, y1, x2, y2 = b.cpu().numpy()
            x1, y1 = max(0, int(x1)), max(0, int(y1))
            x2, y2 = min(w - 1, int(x2)), min(h - 1, int(y2))
            if x2 > x1 and y2 > y1:
                detections.append(([x1, y1, x2 - x1, y2 - y1], float(c), "person"))

    # sanitize detections to avoid NaN/inf values entering the assignment cost matrix
    clean_dets = []
    for det in detections:
        ltwh, conf, cls_name = det
        if len(ltwh) != 4:
            continue
        x, y, w_box, h_box = ltwh
        vals = [x, y, w_box, h_box, conf]
        if not all(np.isfinite(v) for v in vals):
            continue
        if w_box <= 0 or h_box <= 0:
            continue
        clean_dets.append(det)

    try:
        tracks = tracker.update_tracks(clean_dets, frame=frame)
    except Exception as e:
        # Fallback for IoU-only mode when DeepSort has no internal embedder.
        # Use normalized non-zero embeddings (zeros can produce invalid cosine distances).
        if "Embedder not created during init" in str(e):
            base_embed = np.ones(128, dtype=np.float32)
            base_embed /= np.linalg.norm(base_embed)
            dummy_embeds = [base_embed.copy() for _ in clean_dets]
            try:
                tracks = tracker.update_tracks(clean_dets, embeds=dummy_embeds)
            except Exception:
                # Hard fallback: skip this frame instead of crashing the app.
                tracks = []
        else:
            # Hard fallback: skip this frame instead of crashing the app.
            tracks = []
    active_ids = 0
    high_alerts = 0

    for tr in tracks:
        if not tr.is_confirmed():
            continue

        active_ids += 1
        tid = tr.track_id
        x1, y1, x2, y2 = map(int, tr.to_ltrb())
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w - 1, x2), min(h - 1, y2)
        if x2 <= x1 or y2 <= y1:
            continue

        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        if heatmap is not None and 0 <= cx < w and 0 <= cy < h:
            heatmap[cy, cx] += 1

        init_track(track_data, tid, frame_idx, fps)
        td = track_data[tid]
        td["end_frame"] = frame_idx
        td["pos"].append((cx, cy, t_sec))
        td["trail"].append((cx, cy))

        # Age/Gender update
        if enable_age_gender and (frame_idx - td["last_ag_frame"]) >= AGE_GENDER_EVERY_N_FRAMES:
            person_roi = frame[y1:y2, x1:x2]
            ag, gg = estimate_age_gender(person_roi, bbox_h=(y2 - y1), frame_h=h)
            if ag:
                td["ag_votes"].append((ag, gg))
                ages = [a for a, _ in td["ag_votes"] if a is not None]
                gens = [g for _, g in td["ag_votes"] if g is not None]
                if ages:
                    td["age"] = max(set(ages), key=ages.count)
                if gens:
                    td["gender"] = max(set(gens), key=gens.count)
            td["last_ag_frame"] = frame_idx

        # Theft risk
        risk = 0
        reasons = []

        if theft_mode:
            # Loitering
            if len(td["pos"]) >= max(15, int(fps * 5)):
                pts = np.array([(p[0], p[1]) for p in td["pos"]])
                var_sum = np.var(pts, axis=0).sum()
                span = td["pos"][-1][2] - td["pos"][0][2]
                if var_sum < THEFT_CONFIG["zone_var_threshold"] and span >= THEFT_CONFIG["loiter_seconds"]:
                    risk += RISK_WEIGHTS["LOITERING"]
                    reasons.append("LOITERING")

            # Erratic movement
            if len(td["pos"]) >= 8:
                recent = list(td["pos"])[-min(len(td["pos"]), int(max(10, fps * 2))):]
                angles = []
                for i in range(len(recent) - 1):
                    dx = recent[i + 1][0] - recent[i][0]
                    dy = recent[i + 1][1] - recent[i][1]
                    if dx == 0 and dy == 0:
                        continue
                    angles.append(math.atan2(dy, dx))
                changes = sum(
                    1 for i in range(len(angles) - 1)
                    if abs(angles[i + 1] - angles[i]) > math.pi / 3
                )
                if changes >= THEFT_CONFIG["direction_changes_threshold"]:
                    risk += RISK_WEIGHTS["ERRATIC_MOVEMENT"]
                    reasons.append("ERRATIC_MOVEMENT")

            # Exit behavior
            if len(td["pos"]) >= 2:
                p1 = td["pos"][-2]
                p2 = td["pos"][-1]
                dt = max(1e-6, p2[2] - p1[2])
                speed = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) / dt

                if is_near_exit(x1, y1, x2, y2, w, h):
                    time_in = (frame_idx - td["start_frame"]) / fps if fps > 0 else 0
                    if time_in <= THEFT_CONFIG["quick_exit_seconds"]:
                        risk += RISK_WEIGHTS["QUICK_EXIT"]
                        reasons.append("QUICK_EXIT")
                    if speed >= THEFT_CONFIG["high_speed_px_per_sec"]:
                        risk += RISK_WEIGHTS["HIGH_SPEED_NEAR_EXIT"]
                        reasons.append("HIGH_SPEED_NEAR_EXIT")

        td["risk_max"] = max(td["risk_max"], risk)
        for r in reasons:
            td["reasons"].add(r)

        if risk >= 80:
            high_alerts += 1
            if event_log is not None:
                event_log.append({
                    "frame": frame_idx,
                    "time_sec": round(t_sec, 2),
                    "person_id": tid,
                    "risk_score": risk,
                    "reasons": ",".join(reasons),
                })

        # draw
        dur = (td["end_frame"] - td["start_frame"]) / fps if fps > 0 else 0
        age_txt = td["age"] if td["age"] else fallback_age_range(y2 - y1, h)
        gen_txt = td["gender"] if td["gender"] else "Unknown"

        if theft_mode:
            label = f"ID {tid} | {fmt_duration(dur)} | Risk {risk} | {gen_txt}, {age_txt}"
            color = risk_color(risk)
        else:
            label = f"ID {tid} | {fmt_duration(dur)} | {gen_txt}, {age_txt}"
            color = (0, 255, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 2)

        if len(td["trail"]) >= 2:
            pts = np.array(td["trail"], dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], False, (255, 200, 0), 2)

    return frame, active_ids, high_alerts

# ================= Video runner (track/theft) =================
def run_uploaded_video(uploaded_file, theft_mode=False):
    if not HAS_DEEPSORT:
        st.error("Install deep-sort-realtime first.")
        return

    model = get_detect_model()
    tracker = make_tracker(live=False)

    tmp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp_video.write(uploaded_file.read())
    tmp_video.flush()

    cap = cv2.VideoCapture(tmp_video.name)
    if not cap.isOpened():
        st.error("Could not open uploaded video.")
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    out_path = OUT_DIR / f"output_{uuid.uuid4().hex[:8]}.mp4"
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    if not writer.isOpened():
        st.error("Could not create output video.")
        cap.release()
        return

    frame_slot = st.empty()
    prog = st.progress(0)
    c1, c2, c3 = st.columns(3)
    m_active, m_alert, m_prog = c1.empty(), c2.empty(), c3.empty()

    track_data = {}
    event_log = []
    heatmap = np.zeros((h, w), dtype=np.float32)

    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        idx += 1

        out, active, alerts = process_frame(
            frame=frame,
            model=model,
            tracker=tracker,
            track_data=track_data,
            frame_idx=idx,
            fps=fps,
            theft_mode=theft_mode,
            heatmap=heatmap,
            event_log=event_log,
            conf_thres=CONF_THRES,
            enable_age_gender=True
        )
        writer.write(out)

        if idx % 3 == 0:
            frame_slot.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB), channels="RGB", width="stretch")
            m_active.metric("Active IDs", active)
            m_alert.metric("High Alerts", alerts if theft_mode else 0)
            pct = min(100, int(100 * idx / total))
            m_prog.metric("Progress", f"{pct}%")
            prog.progress(pct / 100.0)

    cap.release()
    writer.release()

    # CSVs
    people_df = make_people_df(track_data, fps)
    people_csv = OUT_DIR / f"people_{uuid.uuid4().hex[:8]}.csv"
    events_csv = OUT_DIR / f"events_{uuid.uuid4().hex[:8]}.csv"
    summary_csv = OUT_DIR / f"summary_{uuid.uuid4().hex[:8]}.csv"
    heatmap_csv = OUT_DIR / f"heatmap_{uuid.uuid4().hex[:8]}.csv"

    people_df.to_csv(people_csv, index=False)
    pd.DataFrame(event_log).to_csv(events_csv, index=False)

    summary_df = pd.DataFrame([{
        "Unique_People": int(people_df["Person_ID"].nunique() if len(people_df) else 0),
        "Frames_Processed": idx,
        "FPS": fps,
        "Mode": "Theft Video" if theft_mode else "Track Video",
        "High_Risk_Events": len(event_log)
    }])
    summary_df.to_csv(summary_csv, index=False)

    # Heatmap outputs
    heat_path = OUT_DIR / f"heatmap_{uuid.uuid4().hex[:8]}.png"
    if heatmap.max() > 0:
        blur = cv2.GaussianBlur(heatmap, (0, 0), sigmaX=15, sigmaY=15)
        norm = cv2.normalize(blur, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        heat_img = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
        cv2.imwrite(str(heat_path), heat_img)
    pd.DataFrame(heatmap).to_csv(heatmap_csv, index=False)

    st.success("Processing complete.")
    st.video(str(out_path))

    k1, k2, k3 = st.columns(3)
    k1.metric("Unique People", int(people_df["Person_ID"].nunique() if len(people_df) else 0))
    k2.metric("Frames", idx)
    k3.metric("High-Risk Events", len(event_log))

    st.subheader("People Summary")
    st.dataframe(people_df, width="stretch")

    if heat_path.exists():
        st.subheader("Customer Movement Heatmap")
        st.image(str(heat_path), width="stretch")

    # downloads
    with open(out_path, "rb") as f:
        st.download_button("Download Output Video", f, file_name=out_path.name, mime="video/mp4")
    with open(people_csv, "rb") as f:
        st.download_button("Download People CSV", f, file_name=people_csv.name, mime="text/csv")
    with open(events_csv, "rb") as f:
        st.download_button("Download Events CSV", f, file_name=events_csv.name, mime="text/csv")
    with open(summary_csv, "rb") as f:
        st.download_button("Download Summary CSV", f, file_name=summary_csv.name, mime="text/csv")
    with open(heatmap_csv, "rb") as f:
        st.download_button("Download Heatmap CSV", f, file_name=heatmap_csv.name, mime="text/csv")
    if heat_path.exists():
        with open(heat_path, "rb") as f:
            st.download_button("Download Heatmap PNG", f, file_name=heat_path.name, mime="image/png")

def run_local_webcam_session(duration_sec=LOCAL_WEBCAM_SECONDS_DEFAULT):
    if not HAS_DEEPSORT:
        st.error("Install deep-sort-realtime first.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Could not open webcam (camera busy or permission denied).")
        return

    model = get_detect_model()
    tracker = make_tracker(live=True)
    track_data = {}
    event_log = []

    frame_slot = st.empty()
    c1, c2, c3 = st.columns(3)
    m_active, m_alert, m_people = c1.empty(), c2.empty(), c3.empty()
    prog = st.progress(0)

    start_t = time.time()
    frame_idx = 0
    out_fps = LOCAL_WEBCAM_FPS

    out_path = OUT_DIR / f"live_local_{uuid.uuid4().hex[:8]}.mp4"
    writer = None

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame_idx += 1
            h, w = frame.shape[:2]
            if w > WEBCAM_MAX_WIDTH:
                scale = WEBCAM_MAX_WIDTH / w
                frame = cv2.resize(frame, (WEBCAM_MAX_WIDTH, int(h * scale)))

            if frame_idx % LOCAL_WEBCAM_INFER_EVERY == 0:
                out, active, alerts = process_frame(
                    frame=frame,
                    model=model,
                    tracker=tracker,
                    track_data=track_data,
                    frame_idx=frame_idx,
                    fps=out_fps,
                    theft_mode=True,
                    heatmap=None,
                    event_log=event_log,
                    conf_thres=WEBCAM_CONF_THRES,
                    enable_age_gender=False,
                )
            else:
                out = frame
                active = 0
                alerts = 0

            if writer is None:
                oh, ow = out.shape[:2]
                writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), out_fps, (ow, oh))

            if writer is not None:
                writer.write(out)

            frame_slot.image(cv2.cvtColor(out, cv2.COLOR_BGR2RGB), channels="RGB", width="stretch")
            m_active.metric("Active IDs", int(active))
            m_alert.metric("High Alerts", int(alerts))
            m_people.metric("Unique People", int(len(track_data)))

            elapsed = time.time() - start_t
            p = min(1.0, elapsed / max(1, duration_sec))
            prog.progress(p)
            if elapsed >= duration_sec:
                break

    finally:
        cap.release()
        if writer is not None:
            writer.release()

    people_df = make_people_df(track_data, out_fps)
    people_csv = OUT_DIR / f"live_people_{uuid.uuid4().hex[:8]}.csv"
    events_csv = OUT_DIR / f"live_events_{uuid.uuid4().hex[:8]}.csv"
    people_df.to_csv(people_csv, index=False)
    pd.DataFrame(event_log).to_csv(events_csv, index=False)

    st.success("Local webcam session complete.")
    if out_path.exists():
        st.video(str(out_path))

    st.dataframe(people_df, width="stretch")
    with open(people_csv, "rb") as f:
        st.download_button("Download Live People CSV", f, file_name=people_csv.name, mime="text/csv")
    with open(events_csv, "rb") as f:
        st.download_button("Download Live Events CSV", f, file_name=events_csv.name, mime="text/csv")
    if out_path.exists():
        with open(out_path, "rb") as f:
            st.download_button("Download Live Output Video", f, file_name=out_path.name, mime="video/mp4")

# ================= Live webcam (track + theft simultaneous) =================
if HAS_WEBRTC:
    class LiveProcessor(VideoProcessorBase):
        def __init__(self, model):
            self.model = model
            self.tracker = make_tracker(live=True)
            self.track_data = {}
            self.frame_idx = 0
            self.fps = 25
            self.lock = threading.Lock()
            self.last_active = 0
            self.last_alerts = 0
            self.last_annotated = None
            self.last_infer_ts = 0.0

        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            if img.shape[1] > WEBCAM_MAX_WIDTH:
                scale = WEBCAM_MAX_WIDTH / img.shape[1]
                img = cv2.resize(img, (WEBCAM_MAX_WIDTH, int(img.shape[0] * scale)))
            self.frame_idx += 1

            now = time.time()
            if (now - self.last_infer_ts) >= WEBCAM_INFER_INTERVAL_SEC:
                out, active, alerts = process_frame(
                    frame=img,
                    model=self.model,
                    tracker=self.tracker,
                    track_data=self.track_data,
                    frame_idx=self.frame_idx,
                    fps=self.fps,
                    theft_mode=True,      # webcam does both at once
                    heatmap=None,
                    event_log=None,
                    conf_thres=WEBCAM_CONF_THRES,
                    enable_age_gender=False  # disable in live mode for speed
                )
                self.last_annotated = out
                self.last_infer_ts = now
            else:
                out = self.last_annotated.copy() if self.last_annotated is not None else img.copy()
                active, alerts = self.last_active, self.last_alerts
                cv2.putText(out, "LIVE MODE (LOW-LATENCY)", (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

            with self.lock:
                self.last_active = active
                self.last_alerts = alerts

            return av.VideoFrame.from_ndarray(out, format="bgr24")

        def get_live_stats_df(self):
            with self.lock:
                df = make_people_df(self.track_data, self.fps)
                return self.last_active, self.last_alerts, df

# ================= Sidebar =================
with st.sidebar:
    st.header("Project Status")
    st.write(f"Training done: `{st.session_state.training_done}`")
    st.write(f"Detection model: `{st.session_state.detect_model_path}`")
    st.write(f"Classification model: `{st.session_state.cls_model_path}`")
    if not HAS_DEEPSORT:
        st.warning("deep-sort-realtime missing.")
    if not HAS_DEEPFACE:
        st.warning("DeepFace missing (fallback age range + unknown gender used).")
    if not HAS_WEBRTC:
        st.warning("WebRTC missing (Live Webcam disabled).")

# ================= Main flow =================
if not st.session_state.training_done:
    st.subheader("Step 1: Upload Dataset and Train")
    st.write("Upload ZIP dataset first. After training, Track/Theft/Webcam modes unlock.")

    zf = st.file_uploader("Dataset ZIP", type=["zip"], key="dataset_zip")
    col1, col2 = st.columns(2)
    with col1:
        base_model = st.selectbox("Base classification model", ["yolov8n-cls.pt", "yolov8s-cls.pt"], index=0)
    with col2:
        split_ratio = st.slider("Train split", 0.6, 0.95, 0.8, 0.05)

    if zf is not None and st.button("Start Training"):
        with st.spinner("Training in progress..."):
            try:
                res = train_cls_from_zip_auto(
                    zip_file=zf,
                    base_model=base_model,
                    split_ratio=split_ratio
                )
                st.success("Training complete.")
                st.session_state.training_done = True
                st.session_state.cls_model_path = res["best_path"]

                try:
                    STATE_FILE.write_text(json.dumps({
                        "training_done": True,
                        "cls_model_path": res["best_path"]
                    }))
                except Exception:
                    pass

                st.write(f"Total images: `{res['total_images']}`")
                st.write(f"Used config: `{res['used_config']}`")
                st.write(f"Best model: `{res['best_path']}`")
                st.write(f"Run folder: `{res['save_dir']}`")

                split_df = pd.DataFrame([{"Class": k, **v} for k, v in res["class_stats"].items()])
                st.subheader("Dataset Split Summary")
                st.dataframe(split_df, width="stretch")

                c1, c2 = st.columns(2)
                c1.metric("Top-1 Accuracy", f"{res['top1']:.4f}" if res["top1"] is not None else "N/A")
                c2.metric("Top-5 Accuracy", f"{res['top5']:.4f}" if res["top5"] is not None else "N/A")

                if res["results_csv"] and os.path.exists(res["results_csv"]):
                    logs = pd.read_csv(res["results_csv"])
                    st.subheader("Epoch Logs")
                    st.dataframe(logs.tail(20), width="stretch")
                    if "epoch" in logs.columns:
                        num_cols = [c for c in logs.columns if logs[c].dtype != "O"]
                        plot_cols = [c for c in num_cols if ("loss" in c.lower() or "top1" in c.lower() or "top5" in c.lower())]
                        if plot_cols:
                            st.line_chart(logs.set_index("epoch")[plot_cols])

                st.info("Switching to Step 2...")
                st.rerun()
            except Exception as e:
                st.error(f"Training failed: {e}")

    if st.button("Use Existing Training and Continue to Step 2"):
        st.session_state.training_done = True
        try:
            STATE_FILE.write_text(json.dumps({
                "training_done": True,
                "cls_model_path": st.session_state.cls_model_path
            }))
        except Exception:
            pass
        st.rerun()

    st.stop()

# Step 2
st.subheader("Step 2: Choose Mode")
mode = st.radio("Mode", ["Track Video", "Theft Video", "Live Webcam"], horizontal=True)

if mode in ["Track Video", "Theft Video"]:
    uploaded_video = st.file_uploader("Upload video", type=["mp4", "avi", "mov", "mkv"], key="video_file")
    if uploaded_video is not None and st.button("Run"):
        run_uploaded_video(uploaded_file=uploaded_video, theft_mode=(mode == "Theft Video"))

else:
    st.write("Live webcam runs tracking + theft detection simultaneously.")
    engine = st.radio("Webcam Engine", ["Browser WebRTC", "Built-in Local (no WebRTC)"], horizontal=True)

    if engine == "Browser WebRTC":
        if not HAS_WEBRTC:
            st.error("WebRTC packages missing. Use Built-in Local mode below or install: pip install streamlit-webrtc av")
        elif not HAS_DEEPSORT:
            st.error("Install tracker package: pip install deep-sort-realtime")
        else:
            live_model = get_detect_model()
            try:
                ctx = webrtc_streamer(
                    key="live-webcam",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration=RTC_CFG,
                    media_stream_constraints={
                        "video": {
                            "width": {"ideal": 640},
                            "height": {"ideal": 360},
                            "frameRate": {"ideal": 12, "max": 15},
                        },
                        "audio": False,
                    },
                    video_processor_factory=lambda: LiveProcessor(live_model),
                    async_processing=True,
                )
                if ctx.video_processor and st.button("Refresh Live Stats"):
                    active, alerts, live_df = ctx.video_processor.get_live_stats_df()
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Active IDs", active)
                    c2.metric("High Alerts", alerts)
                    c3.metric("Unique People", int(live_df["Person_ID"].nunique() if len(live_df) else 0))
                    st.dataframe(live_df, width="stretch")

                    live_csv = OUT_DIR / f"live_people_{uuid.uuid4().hex[:8]}.csv"
                    live_df.to_csv(live_csv, index=False)
                    with open(live_csv, "rb") as f:
                        st.download_button("Download Live CSV", f, file_name=live_csv.name, mime="text/csv")
            except Exception as e:
                st.error(f"WebRTC failed: {e}")

    else:
        duration_sec = st.slider("Local webcam session duration (seconds)", 15, 180, LOCAL_WEBCAM_SECONDS_DEFAULT, 5)
        st.caption("Runs directly inside app.py without WebRTC. Use this if browser webcam is not opening.")
        if st.button("Start Local Webcam Session"):
            run_local_webcam_session(duration_sec=duration_sec)
