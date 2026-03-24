# ============================================================
# YolcuSayar - Ana Script
# YOLOv5-Nano + DeepSORT + Çizgi Sayımı
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
    mqtt_client = mqtt.Client()
    mqtt_client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    mqtt_client.loop_start()


def publish_mqtt(counts: dict):
    if config.MQTT_ENABLED:
        payload = json.dumps(counts)
        mqtt_client.publish(config.MQTT_TOPIC, payload)


def main():
    # --- Model ve Tracker ---
    print("[YolcuSayar] Model yükleniyor...")
    model   = YOLO(config.MODEL_PATH)
    tracker = DeepSort(max_age=config.MAX_AGE, n_init=config.N_INIT)
    counter = LineCounter(line_y=config.LINE_Y)

    # --- Video Kaynağı ---
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)
    if not cap.isOpened():
        print("[HATA] Video kaynağı açılamadı:", config.VIDEO_SOURCE)
        return

    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_cap = cap.get(cv2.CAP_PROP_FPS) or 20

    # --- Video Yazıcı ---
    out = cv2.VideoWriter(
        config.OUTPUT_PATH,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps_cap, (W, H)
    )

    print(f"[YolcuSayar] Çalışıyor | Çizgi Y={config.LINE_Y} | Kaynak={config.VIDEO_SOURCE}")
    frame_count = 0
    t_start = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # --- YOLO Tespiti ---
        results    = model(frame, verbose=False, conf=config.CONF_THRESH, iou=config.IOU_THRESH)
        detections = []

        for box in results[0].boxes:
            if int(box.cls) != 0:          # sadece 'person' sınıfı (cls=0)
                continue
            conf = float(box.conf)
            if conf < config.CONF_THRESH:
                continue
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            w = x2 - x1
            h = y2 - y1
            detections.append(([x1, y1, w, h], conf, 'person'))

        # --- DeepSORT Takip ---
        tracks = tracker.update_tracks(detections, frame=frame)

        for track in tracks:
            if not track.is_confirmed():
                continue

            tid        = track.track_id
            x1, y1, x2, y2 = map(int, track.to_ltrb())
            cx         = int((x1 + x2) / 2)
            cy         = int((y1 + y2) / 2)

            # Sayım
            event = counter.update(tid, cx, cy)

            # Renk: bindi=yeşil, indi=kırmızı, normal=mavi
            color = (255, 200, 0)
            if event == "bindi":
                color = (0, 255, 0)
            elif event == "indi":
                color = (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.circle(frame, (cx, cy), 4, color, -1)
            cv2.putText(frame, f"ID:{tid}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # --- Çizgi ve Sayı ---
        cv2.line(frame, (0, config.LINE_Y), (W, config.LINE_Y), (0, 255, 255), 2)

        counts = counter.get_counts()
        elapsed = time.time() - t_start
        fps_real = frame_count / elapsed if elapsed > 0 else 0

        cv2.putText(frame, f"Bindi: {counts['bindi']}  Indi: {counts['indi']}  Net: {counts['net']}",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
        cv2.putText(frame, f"FPS: {fps_real:.1f}",
                    (W - 120, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        # --- Kaydet ---
        out.write(frame)

        if config.SHOW_VIDEO:
            cv2.imshow("YolcuSayar", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[YolcuSayar] Kullanıcı tarafından durduruldu.")
                break

        # MQTT: her 30 frame'de bir yayınla
        if frame_count % 30 == 0:
            publish_mqtt({**counts, "timestamp": time.time()})

    # --- Log Kaydet ---
    final = {**counter.get_counts(), "timestamp": time.time(), "frames": frame_count}
    with open(config.LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    print("[YolcuSayar] Log kaydedildi:", config.LOG_PATH)
    print(f"[YolcuSayar] Sonuç → Bindi: {final['bindi']}  |  İndi: {final['indi']}  |  Net: {final['net']}")

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
