# ============================================================
# YolcuSayar - Konfigürasyon Dosyası
# ============================================================

# --- Video / Kamera ---
VIDEO_SOURCE = 0              # 0 = webcam, veya "videos/test.mp4"
OUTPUT_PATH  = "outputs/output.mp4"
LOG_PATH     = "outputs/count_log.json"

# --- Model ---
MODEL_PATH   = "models/yolov5n.pt"   # İlk çalıştırmada otomatik indirilir
CONF_THRESH  = 0.4                    # Tespit güven eşiği (0.0 - 1.0)
IOU_THRESH   = 0.45

# --- Sayım Çizgisi ---
# Kameraya göre ayarla. Görüntü yüksekliğinin ortası genellikle iyi çalışır.
# Örnek: 480p için 240, 720p için 360
LINE_Y       = 350

# --- Tracker ---
MAX_AGE      = 30     # Kaç frame sonra kayıp track silinsin
N_INIT       = 3      # Kaç frame görünce track onaylansın

# --- MQTT (opsiyonel, Raspberry Pi → bulut) ---
MQTT_ENABLED = False
MQTT_BROKER  = "broker.hivemq.com"
MQTT_PORT    = 1883
MQTT_TOPIC   = "yolcusayar/sayim"

# --- Görselleştirme ---
SHOW_VIDEO   = True   # Raspberry Pi'de False yapabilirsin (headless)
