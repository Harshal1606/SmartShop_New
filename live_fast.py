import cv2
import math
import time
import numpy as np
from collections import defaultdict, deque
from ultralytics import YOLO

# ---------------- Models ----------------
DETECT_MODEL = "yolov8n.pt"   # person detection+tracking
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ---------------- Runtime config ----------------
CONF = 0.28
FRAME_W = 640
INFER_EVERY = 2
WARMUP_SEC = 5.0

# Normalized motion thresholds (stable across distance)
SPEED_NORM_FAST = 0.24
ACCEL_NORM_FAST = 0.20
DIR_CHANGE_ANGLE = math.pi / 2.8
DIR_CHANGES_THRESH = 5

# Loitering
LOITER_SEC = 8.0
LOITER_VAR = 35.0

# Exit zone
NEAR_EXIT_X = 0.08
NEAR_EXIT_Y = 0.90
QUICK_EXIT_SEC = 7.0

# Concealment/back-facing proxies
AREA_JUMP_RATIO = 0.18
ASPECT_JUMP_RATIO = 0.15
CONCEAL_WINDOW_SEC = 1.2
BACK_NOFACE_SEC = 2.0
FACE_CHECK_EVERY = 4  # frames

# Risk logic
RISK_DECAY_PER_FRAME = 1.2
RISK_ALERT = 70

RISK_INC = {
    "LOITERING": 10,
    "ERRATIC_PATH": 14,
    "FAST_MOVE": 16,
    "SUDDEN_ACCEL": 12,
    "QUICK_EXIT": 20,
    "CONCEALMENT_PROXY": 28,
    "BACK_FACING": 12,
    "HIDE_AND_MOVE": 30,
}

# Counter requirements to avoid false alarms
CNT_REQ = {
    "FAST_MOVE": 4,
    "SUDDEN_ACCEL": 4,
    "ERRATIC_PATH": 3,
    "LOITERING": 3,
    "QUICK_EXIT": 3,
    "CONCEALMENT_PROXY": 2,
    "BACK_FACING": 2,
}

# ---------------- Helpers ----------------
def risk_color(score):
    if score < 25: return (0, 255, 0)
    if score < 55: return (0, 255, 255)
    if score < 75: return (0, 165, 255)
    return (0, 0, 255)

def risk_state(score):
    if score < 25: return "NORMAL"
    if score < 55: return "MONITOR"
    if score < 75: return "SUSPICIOUS"
    return "ALERT"

def near_exit(x1, y1, x2, y2, w, h):
    return (
        x1 < int(NEAR_EXIT_X * w)
        or x2 > int((1 - NEAR_EXIT_X) * w)
        or y2 > int(NEAR_EXIT_Y * h)
    )

def safe_div(a, b):
    return a / b if b > 1e-6 else 0.0

def face_visible_score(person_roi):
    if person_roi is None or person_roi.size == 0:
        return 0.0
    gray = cv2.cvtColor(person_roi, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(35, 35))
    if len(faces) == 0:
        return 0.0
    # confidence proxy by largest face area ratio
    h, w = gray.shape[:2]
    fa = max([fw * fh for (_, _, fw, fh) in faces])
    return fa / max(1.0, (w * h))

# ---------------- Init ----------------
model = YOLO(DETECT_MODEL)
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Webcam not available")

track_data = defaultdict(lambda: {
    "start_t": time.time(),
    "last_t": time.time(),
    "pos": deque(maxlen=180),          # (cx, cy, t)
    "bbox": deque(maxlen=90),          # (w, h, area, aspect, t)
    "diag": deque(maxlen=60),
    "face_vis": deque(maxlen=60),      # (score, t)
    "risk": 0.0,
    "risk_max": 0.0,
    "reasons": deque(maxlen=8),

    # counters
    "cnt_fast": 0,
    "cnt_accel": 0,
    "cnt_err": 0,
    "cnt_loiter": 0,
    "cnt_exit": 0,
    "cnt_conceal": 0,
    "cnt_back": 0,

    # event memory
    "last_conceal_t": None,
    "had_face_once": False,
})

frame_idx = 0
last_results = None
start_app = time.time()

print("Press q to quit")

# ---------------- Loop ----------------
while True:
    ok, frame = cap.read()
    if not ok:
        break

    h0, w0 = frame.shape[:2]
    if w0 > FRAME_W:
        s = FRAME_W / w0
        frame = cv2.resize(frame, (FRAME_W, int(h0 * s)))

    h, w = frame.shape[:2]
    frame_idx += 1

    if frame_idx % INFER_EVERY == 0:
        last_results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],
            conf=CONF,
            verbose=False
        )

    canvas = frame.copy()

    if last_results is not None and len(last_results) > 0:
        r = last_results[0]
        boxes = r.boxes
        if boxes is not None and boxes.xyxy is not None and len(boxes.xyxy) > 0:
            ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [-1] * len(boxes.xyxy)
            xyxy = boxes.xyxy.int().cpu().tolist()

            for tid, b in zip(ids, xyxy):
                if tid < 0:
                    continue

                x1, y1, x2, y2 = b
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w - 1, x2), min(h - 1, y2)
                if x2 <= x1 or y2 <= y1:
                    continue

                now = time.time()
                td = track_data[tid]
                td["last_t"] = now

                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                bw, bh = (x2 - x1), (y2 - y1)
                area = float(bw * bh)
                aspect = safe_div(bw, max(1.0, bh))
                diag = math.hypot(bw, bh)

                td["pos"].append((cx, cy, now))
                td["bbox"].append((bw, bh, area, aspect, now))
                td["diag"].append(diag)

                # risk decay always
                td["risk"] = max(0.0, td["risk"] - RISK_DECAY_PER_FRAME)

                if now - start_app < WARMUP_SEC:
                    cv2.rectangle(canvas, (x1, y1), (x2, y2), (120, 255, 120), 2)
                    cv2.putText(canvas, f"ID {tid} | WARMUP", (x1, max(20, y1 - 8)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (120, 255, 120), 2)
                    continue

                # -------- face visibility check --------
                if frame_idx % FACE_CHECK_EVERY == 0:
                    roi = frame[y1:y2, x1:x2]
                    fscore = face_visible_score(roi)
                    td["face_vis"].append((fscore, now))
                    if fscore > 0.015:
                        td["had_face_once"] = True

                # -------- kinematics --------
                speed_n = 0.0
                accel_n = 0.0

                if len(td["pos"]) >= 3:
                    x_prev, y_prev, t_prev = td["pos"][-2]
                    x_prev2, y_prev2, t_prev2 = td["pos"][-3]
                    dt = max(1e-3, now - t_prev)
                    dt2 = max(1e-3, t_prev - t_prev2)

                    d = math.hypot(cx - x_prev, cy - y_prev)
                    d2 = math.hypot(x_prev - x_prev2, y_prev - y_prev2)

                    med_diag = np.median(td["diag"]) if len(td["diag"]) else max(diag, 1.0)
                    speed_n = safe_div(d / dt, med_diag)
                    speed_n_prev = safe_div(d2 / dt2, med_diag)
                    accel_n = abs(speed_n - speed_n_prev)

                # -------- counters --------
                td["cnt_fast"] = td["cnt_fast"] + 1 if speed_n > SPEED_NORM_FAST else max(0, td["cnt_fast"] - 1)
                td["cnt_accel"] = td["cnt_accel"] + 1 if accel_n > ACCEL_NORM_FAST else max(0, td["cnt_accel"] - 1)

                # erratic
                if len(td["pos"]) >= 10:
                    recent = list(td["pos"])[-20:]
                    angs = []
                    for i in range(len(recent) - 1):
                        dx = recent[i + 1][0] - recent[i][0]
                        dy = recent[i + 1][1] - recent[i][1]
                        if dx == 0 and dy == 0:
                            continue
                        angs.append(math.atan2(dy, dx))
                    ch = sum(1 for i in range(len(angs) - 1) if abs(angs[i + 1] - angs[i]) > DIR_CHANGE_ANGLE)
                    td["cnt_err"] = td["cnt_err"] + 1 if ch >= DIR_CHANGES_THRESH else max(0, td["cnt_err"] - 1)

                # loiter
                if len(td["pos"]) >= 25:
                    pts = np.array([(p[0], p[1]) for p in td["pos"]], dtype=np.float32)
                    var_sum = np.var(pts, axis=0).sum()
                    span = td["pos"][-1][2] - td["pos"][0][2]
                    cond = (span >= LOITER_SEC) and (var_sum < LOITER_VAR)
                    td["cnt_loiter"] = td["cnt_loiter"] + 1 if cond else max(0, td["cnt_loiter"] - 1)

                # quick exit
                time_in = now - td["start_t"]
                cond_exit = near_exit(x1, y1, x2, y2, w, h) and time_in <= QUICK_EXIT_SEC and speed_n > (SPEED_NORM_FAST * 0.85)
                td["cnt_exit"] = td["cnt_exit"] + 1 if cond_exit else max(0, td["cnt_exit"] - 1)

                # concealment proxy (shape jump in short window with low center move)
                if len(td["bbox"]) >= 4 and len(td["pos"]) >= 4:
                    _, _, a_old, asp_old, t_old = td["bbox"][-4]
                    _, _, a_new, asp_new, t_new = td["bbox"][-1]

                    if (t_new - t_old) <= CONCEAL_WINDOW_SEC:
                        area_jump = abs(a_new - a_old) / max(1.0, a_old)
                        asp_jump = abs(asp_new - asp_old) / max(1e-3, asp_old)

                        x_old, y_old, _ = td["pos"][-4]
                        center_move = math.hypot(cx - x_old, cy - y_old)

                        # concealment-like: torso shape changes but not much walking
                        cond_conceal = (area_jump > AREA_JUMP_RATIO) and (asp_jump > ASPECT_JUMP_RATIO) and (center_move < 45)
                        td["cnt_conceal"] = td["cnt_conceal"] + 1 if cond_conceal else max(0, td["cnt_conceal"] - 1)

                # back-facing suspicious (only if face existed earlier)
                if td["had_face_once"] and len(td["face_vis"]) >= 3:
                    recent_face = list(td["face_vis"])[-3:]
                    no_face_all = all(fs < 0.01 for fs, _ in recent_face)
                    span_face = recent_face[-1][1] - recent_face[0][1]
                    cond_back = no_face_all and span_face >= BACK_NOFACE_SEC
                    td["cnt_back"] = td["cnt_back"] + 1 if cond_back else max(0, td["cnt_back"] - 1)

                # -------- apply risk only when sustained --------
                reasons_now = []

                if td["cnt_loiter"] >= CNT_REQ["LOITERING"]:
                    td["risk"] += RISK_INC["LOITERING"]
                    td["cnt_loiter"] = 0
                    reasons_now.append("LOITERING")

                if td["cnt_err"] >= CNT_REQ["ERRATIC_PATH"]:
                    td["risk"] += RISK_INC["ERRATIC_PATH"]
                    td["cnt_err"] = 0
                    reasons_now.append("ERRATIC_PATH")

                if td["cnt_fast"] >= CNT_REQ["FAST_MOVE"]:
                    td["risk"] += RISK_INC["FAST_MOVE"]
                    td["cnt_fast"] = 0
                    reasons_now.append("FAST_MOVE")

                if td["cnt_accel"] >= CNT_REQ["SUDDEN_ACCEL"]:
                    td["risk"] += RISK_INC["SUDDEN_ACCEL"]
                    td["cnt_accel"] = 0
                    reasons_now.append("SUDDEN_ACCEL")

                if td["cnt_exit"] >= CNT_REQ["QUICK_EXIT"]:
                    td["risk"] += RISK_INC["QUICK_EXIT"]
                    td["cnt_exit"] = 0
                    reasons_now.append("QUICK_EXIT")

                if td["cnt_conceal"] >= CNT_REQ["CONCEALMENT_PROXY"]:
                    td["risk"] += RISK_INC["CONCEALMENT_PROXY"]
                    td["cnt_conceal"] = 0
                    td["last_conceal_t"] = now
                    reasons_now.append("CONCEALMENT_PROXY")

                if td["cnt_back"] >= CNT_REQ["BACK_FACING"]:
                    td["risk"] += RISK_INC["BACK_FACING"]
                    td["cnt_back"] = 0
                    reasons_now.append("BACK_FACING")

                # hide-and-move combo (strong signal)
                if td["last_conceal_t"] is not None:
                    if (now - td["last_conceal_t"] <= 8.0) and (speed_n > SPEED_NORM_FAST or cond_exit):
                        td["risk"] += RISK_INC["HIDE_AND_MOVE"]
                        td["last_conceal_t"] = None
                        reasons_now.append("HIDE_AND_MOVE")

                if reasons_now:
                    td["reasons"].append(",".join(reasons_now))

                td["risk"] = min(100.0, td["risk"])
                td["risk_max"] = max(td["risk_max"], td["risk"])
                score = int(td["risk"])
                color = risk_color(score)

                cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
                cv2.putText(canvas, f"ID {tid} | {risk_state(score)} | Risk {score}",
                            (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

                if len(td["reasons"]) > 0:
                    cv2.putText(canvas, td["reasons"][-1], (x1, min(h - 10, y2 + 18)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

    cv2.putText(canvas, "STABLE LIVE MODE (q to quit)", (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)

    cv2.imshow("SmartShop Live Stable", canvas)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
