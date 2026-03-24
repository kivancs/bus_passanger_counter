# ============================================================
# YolcuSayar - Streamlit Web Arayüzü
# Çalıştırmak için: streamlit run web/app.py
# ============================================================

import streamlit as st
import json
import time
import os

LOG_PATH = "outputs/count_log.json"

st.set_page_config(
    page_title="YolcuSayar",
    page_icon="🚌",
    layout="centered"
)

st.title("🚌 YolcuSayar — Yolcu Sayım Paneli")
st.caption("Artvin Çoruh Üniversitesi | Bitirme Projesi")

st.divider()

# Otomatik yenile butonu
auto_refresh = st.toggle("Otomatik Yenile (5sn)", value=False)

def load_log():
    if not os.path.exists(LOG_PATH):
        return None
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_log()

if data is None:
    st.warning("Henüz veri yok. `yolcu_sayar.py` çalıştırıldıktan sonra veriler burada görünür.")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="🟢 Bindi", value=data.get("bindi", 0))
    with col2:
        st.metric(label="🔴 İndi", value=data.get("indi", 0))
    with col3:
        net = data.get("net", 0)
        st.metric(label="🔵 Araçtaki (Net)", value=net)

    st.divider()

    ts = data.get("timestamp")
    if ts:
        st.caption(f"Son güncelleme: {time.strftime('%H:%M:%S', time.localtime(ts))}")

    frames = data.get("frames")
    if frames:
        st.caption(f"Toplam işlenen kare: {frames}")

if auto_refresh:
    time.sleep(5)
    st.rerun()
