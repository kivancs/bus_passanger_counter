# ============================================================
# YolcuSayar - Ana Script
# YOLOv5-Nano + DeepSORT + ID Framing + Çizgi Sayımı
#
# Çalıştır: python yolcu_sayar.py
# Kalibre:  İlk açılışta çizgiyi fare ile sürükle, 's' ile kaydet
# ============================================================

import cv2
import json
import time
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

import config
from utils.line_counter import LineCounter

# --- Opsiyonel MQTT ---
if config.MQTT_ENABLED:
    import paho.mqtt.client as mqtt
    _mqtt = mqtt.Client()
    _mqtt.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    _mqtt.loop_start()

def publish_mqtt(counts: dict):
    if config.MQTT_ENABLED:
        _mqtt.publish(config.MQTT_TOPIC, json.dumps(counts))

# ============================================================
# Çizgi Kalibrasyonu — fare ile sürükle
# ============================================================
_drag_line_y = None
_dragging    = False

def _mouse_cb(event, x, y, flags, param):
    global _drag_line_y, _dragging
    if event == cv2.EVENT_LBUTTONDOWN:
        _dragging = True
    if event == cv2.EVENT_MOUSEMOVE and _dragging:
        _drag_line_y = y
    if event == cv2.EVENT_LBUTTONUP:
        _dragging = False

# ============================================================
# Yardımcı: overlay çiz
# ============================================================
def draw_overlay(frame, W, H, line_y, counts, fps, capacity):
    # Sayım çizgisi
    cv2.line(frame, (0, line_y), (W, line_y), (0, 220, 255), 2)
    cv2.putText(frame, "SAYIM CIZGISI", (W // 2 - 80, line_y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 220, 255), 1)

    # Üst bilgi şeridi (yarı saydam)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (W, 60), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    bindi = counts['bindi']
    indi  = counts['indi']
    net   = counts['net']
    dolu  = min(net, capacity)

    cv2.putText(frame, f"BINDI:{bindi}", (10, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 100), 2)
    cv2.putText(frame, f"INDI:{indi}", (160, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 100, 255), 2)
    cv2.putText(frame, f"ARACTAKI:{dolu}/{capacity}", (290, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 220, 0), 2)
    cv2.putText(frame, f"FPS:{fps:.1f}", (W - 100, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 180, 180), 1)

    # Alt bilgi
    cv2.putText(frame, "[Q] Cik  [S] Cizgiyi Kaydet  [R] Sifirla",
                (10, H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

# ============================================================
# Ana döngü
# ============================================================
def main():
    global _drag_line_y

    print("[YolcuSayar] Model yükleniyor...")
    model   = YOLO(config.MODEL_PATH)
    tracker = DeepSort(max_age=config.MAX_AGE, n_init=config.N_INIT)

    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    if not cap.isOpened():
        print("[HATA] Video kaynağı açılamadı:", config.VIDEO_SOURCE)
        return

    W       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_cap = cap.get(cv2.CAP_PROP_FPS) or 20

    # Çizgi başlangıç pozisyonu: config'deki oran × görüntü yüksekliği
    line_y = int(H * config.LINE_Y_RATIO)
    _drag_line_y = line_y

    counter = LineCounter(line_y=line_y)

    out = cv2.VideoWriter(
        config.OUTPUT_PATH,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps_cap, (W, H)
    )

    if config.SHOW_VIDEO:
        cv2.namedWindow("YolcuSayar")
        cv2.setMouseCallback("YolcuSayar", _mouse_cb)

    print(f"[YolcuSayar] Çalışıyor | {W}x{H} | Çizgi Y={line_y} ({config.LINE_Y_RATIO*100:.0f}%)")
    print("  Fare ile çizgiyi sürükle → 'S' ile kaydet | 'R' ile sıfırla | 'Q' çık")

    frame_count = 0
    t_start     = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        # Çizgi fare ile taşındıysa counter'ı güncelle
        if _drag_line_y != line_y:
            line_y = _drag_line_y
            counter.line_y = line_y

        # ── YOLO tespiti ──────────────────────────────────────
        results    = model(frame, verbose=False,
                           conf=config.CONF_THRESH, iou=config.IOU_THRESH)
        detections = []
        for box in results[0].boxes:
            if int(box.cls) != 0:          # sadece person
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append(([x1, y1, x2 - x1, y2 - y1],
                                float(box.conf), 'person'))

        # ── DeepSORT takip ────────────────────────────────────
        tracks = tracker.update_tracks(detections, frame=frame)

        for track in tracks:
            if not track.is_confirmed():
                continue

            tid             = track.track_id
            x1, y1, x2, y2 = map(int, track.to_ltrb())
            cx              = int((x1 + x2) / 2)
            cy              = int((y1 + y2) / 2)

            event = counter.update(tid, cx, cy)

            # ── ID Kutusu rengi ───────────────────────────────
            if event == "bindi":
                box_color  = (0, 255, 80)    # parlak yeşil
                label_bg   = (0, 180, 50)
            elif event == "indi":
                box_color  = (0, 80, 255)    # parlak kırmızı
                label_bg   = (0, 50, 200)
            else:
                box_color  = (255, 180, 0)   # turuncu (takip ediliyor)
                label_bg   = (180, 120, 0)

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

            # Merkez nokta
            cv2.circle(frame, (cx, cy), 5, box_color, -1)

            # ID etiketi (arka planlı)
            label      = f"ID:{tid}"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(frame, (x1, y1 - lh - 10), (x1 + lw + 6, y1), label_bg, -1)
            cv2.putText(frame, label, (x1 + 3, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # ── Overlay ───────────────────────────────────────────
        elapsed  = time.time() - t_start
        fps_real = frame_count / elapsed if elapsed > 0 else 0
        draw_overlay(frame, W, H, line_y,
                     counter.get_counts(), fps_real, config.MAX_CAPACITY)

        out.write(frame)

        if config.SHOW_VIDEO:
            cv2.imshow("YolcuSayar", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("[YolcuSayar] Çıkılıyor...")
                break
            elif key == ord('s'):
                config.LINE_Y_RATIO = round(line_y / H, 3)
                print(f"[YolcuSayar] Çizgi kaydedildi: Y={line_y} (oran={config.LINE_Y_RATIO})")
            elif key == ord('r'):
                counter.reset()
                print("[YolcuSayar] Sayaç sıfırlandı.")

        # MQTT: her 30 frame'de bir
        if frame_count % 30 == 0:
            publish_mqtt({**counter.get_counts(), "timestamp": time.time()})

    # ── Log kaydet ────────────────────────────────────────────
    final = {
        **counter.get_counts(),
        "timestamp": time.time(),
        "frames":    frame_count,
        "line_y":    line_y,
        "line_ratio": round(line_y / H, 3)
    }
    with open(config.LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"[YolcuSayar] Bitti → Bindi:{final['bindi']}  İndi:{final['indi']}  Net:{final['net']}")

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

