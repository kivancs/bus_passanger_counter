# ============================================================
# YolcuSayar - Konfigürasyon Dosyası
# ============================================================

# --- Video / Kamera ---
VIDEO_SOURCE = 0              # 0 = webcam, veya "videos/test.mp4"
OUTPUT_PATH  = "outputs/output.mp4"
LOG_PATH     = "outputs/count_log.json"

# --- Model ---
# "yolov5n.pt" → ultralytics tarafından otomatik indirilir, elle indirmene gerek yok
MODEL_PATH   = "yolov5n.pt"
CONF_THRESH  = 0.4            # Tespit güven eşiği (0.0 - 1.0)
IOU_THRESH   = 0.45

# --- Sayım Çizgisi ---
#
#  Kamera görüntüsü (kapıya bakıyor, ~30° açı):
#
#  Y=0   ┌─────────────────────────┐
#        │   (üst, araç içi)       │
#        │                         │
#  Y=0.4 │ ════════════════════════│ ← LINE_Y_RATIO = 0.4
#        │   (kapı eşiği bölgesi)  │   Kişi bu çizgiyi geçince sayılır
#        │                         │
#  Y=1.0 └─────────────────────────┘
#           (alt, dışarısı/basamak)
#
#  LINE_Y_RATIO: 0.0 (en üst) → 1.0 (en alt)
#  Kamera kapıya tam karşıdan bakıyorsa: 0.5 (tam orta)
#  Kamera yukarıdan bakıyorsa: 0.4 daha iyi çalışır
#  İlk çalıştırmada ekranda çizgiyi göreceksin, 's' tuşuyla kaydet
LINE_Y_RATIO = 0.5            # Görüntü yüksekliğinin yüzde kaçında çizgi olsun

# --- Tracker ---
MAX_AGE      = 30     # Kaç frame sonra kayıp track silinsin
N_INIT       = 3      # Kaç frame görünce track onaylansın

# --- Araç Kapasitesi ---
MAX_CAPACITY = 20

# --- MQTT (opsiyonel, Raspberry Pi → bulut) ---
MQTT_ENABLED = False
MQTT_BROKER  = "broker.hivemq.com"
MQTT_PORT    = 1883
MQTT_TOPIC   = "yolcusayar/sayim"

# --- Görselleştirme ---
SHOW_VIDEO   = True   # Raspberry Pi'de False yapabilirsin (headless)
