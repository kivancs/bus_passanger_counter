# ============================================================
# YolcuSayar - Streamlit Web Arayüzü
# Çalıştırmak için: streamlit run web/app.py
# ============================================================

import streamlit as st
import json
import time
import os

LOG_PATH = "outputs/count_log.json"

# ── Seed verisi ──────────────────────────────────────────────
SEED = {
    "max_capacity": 20,
    "initial_stats": {
        "current_passengers": 12,
        "total_in":           45,
        "total_out":          33,
        "time_labels":        ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00"],
        "occupancy_history":  [5, 15, 20, 12, 8, 14]
    }
}

st.set_page_config(
    page_title="YolcuSayar",
    page_icon="🚌",
    layout="wide"
)

# ── Başlık ────────────────────────────────────────────────────
st.markdown("## 🚌 YolcuSayar — Yolcu Sayım Paneli")
st.caption("Artvin Çoruh Üniversitesi | Bilgisayar Mühendisliği Bitirme Projesi")
st.divider()

auto_refresh = st.toggle("🔄 Otomatik Yenile (5sn)", value=False)

# ── Log yükle (yoksa seed kullan) ────────────────────────────
def load_data():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {
            "bindi":    raw.get("bindi", 0),
            "indi":     raw.get("indi",  0),
            "net":      raw.get("net",   0),
            "frames":   raw.get("frames", 0),
            "timestamp":raw.get("timestamp"),
            "from_seed": False
        }
    # Seed verisiyle doldur
    s = SEED["initial_stats"]
    return {
        "bindi":     s["total_in"],
        "indi":      s["total_out"],
        "net":       s["current_passengers"],
        "frames":    None,
        "timestamp": None,
        "from_seed": True,
        "time_labels":       s["time_labels"],
        "occupancy_history": s["occupancy_history"]
    }

data     = load_data()
capacity = SEED["max_capacity"]
net      = data["net"]
doluluk  = min(int(net / capacity * 100), 100)

# ── Üst metrikler ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("🟢 Toplam Bindi",    data["bindi"])
c2.metric("🔴 Toplam İndi",     data["indi"])
c3.metric("🔵 Şu An Araçta",    f"{net} / {capacity}")
c4.metric("📊 Doluluk",         f"%{doluluk}")

st.divider()

# ── Doluluk barı ──────────────────────────────────────────────
bar_color = "normal" if doluluk < 80 else ("off" if doluluk >= 100 else "inverse")
st.progress(doluluk / 100, text=f"Kapasite: {net}/{capacity} yolcu  (%{doluluk})")

st.divider()

# ── Saatlik doluluk grafiği ───────────────────────────────────
st.subheader("📈 Saatlik Doluluk Geçmişi")

if data.get("from_seed"):
    import pandas as pd
    chart_data = pd.DataFrame({
        "Saat":    data["time_labels"],
        "Yolcu":   data["occupancy_history"]
    }).set_index("Saat")
    st.line_chart(chart_data)
    st.caption("⚠️ Gösterilen veri örnek seed verisidir. `yolcu_sayar.py` çalıştıktan sonra gerçek veriler görünür.")
else:
    st.info("Gerçek zamanlı grafik için çok sayıda log kaydı gerekir.")

st.divider()

# ── Alt bilgi ─────────────────────────────────────────────────
ts = data.get("timestamp")
if ts:
    st.caption(f"Son güncelleme: {time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(ts))}")
if data.get("frames"):
    st.caption(f"İşlenen kare: {data['frames']}")

if auto_refresh:
    time.sleep(5)
    st.rerun()
