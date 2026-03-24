# YolcuSayar 🚌

Araç içi gerçek zamanlı yolcu sayım sistemi.  
**YOLOv5-Nano + DeepSORT + Streamlit**

Artvin Çoruh Üniversitesi — Bilgisayar Mühendisliği Bitirme Projesi

---

## Kurulum

```bash
pip install -r requirements.txt
```

---

## Çalıştırma

### 1. Ana sayım scripti
```bash
python yolcu_sayar.py
```

### 2. Web arayüzü (ayrı terminalde)
```bash
streamlit run web/app.py
```

---

## config.py Ayarları

| Parametre | Açıklama | Varsayılan |
|-----------|----------|-----------|
| `VIDEO_SOURCE` | 0=webcam, "videos/test.mp4"=dosya | `0` |
| `LINE_Y` | Sayım çizgisinin Y koordinatı | `350` |
| `CONF_THRESH` | YOLO güven eşiği | `0.4` |
| `SHOW_VIDEO` | Ekranda göster (Pi'de False yap) | `True` |
| `MQTT_ENABLED` | MQTT yayını aktif et | `False` |

---

## Dosya Yapısı

```
YolcuSayar/
├── yolcu_sayar.py       ← Ana script
├── config.py            ← Tüm ayarlar
├── requirements.txt
├── models/              ← yolov5n.pt buraya
├── videos/              ← test videoları
├── outputs/             ← çıktı video ve JSON
├── utils/
│   └── line_counter.py  ← Sayım mantığı
└── web/
    └── app.py           ← Streamlit dashboard
```
