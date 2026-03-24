from flask import Flask, render_template, jsonify, Response
import json
import random # Simülasyon verisi üretmek için
import os
import time

app = Flask(__name__)

# --- VERİ KAYNAĞINI SOYUTLAMA (SEED DATA'DAN ÇEKME) ---
def get_seed_data():
    # 'seed_data.json' dosyasının konumunu bul (web klasörünün bir üst dizini)
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'seed_data.json')
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError): 
        # Eğer dosya yoksa veya içi boşsa sistem çökmesin diye varsayılan değerler
        print(f"Uyarı: {json_file_path} okunamadı. Varsayılan veriler kullanılıyor.")
        return {
            "max_capacity": 20,
            "initial_stats": {
                "current_passengers": 0, "total_in": 0, "total_out": 0,
                "time_labels": [], "occupancy_history": []
            }
        }

# Sunucu başlarken verileri JSON'dan çek
all_data = get_seed_data()
MAX_CAPACITY = all_data['max_capacity']
vehicle_stats = all_data['initial_stats']


# --- WEB SAYFASI (ARAYÜZ) ROTASI ---
@app.route('/')
def index():
    # Araç doluluk yüzdesini hesapla
    if vehicle_stats["current_passengers"] is not None and MAX_CAPACITY > 0:
        vehicle_stats["occupancy_rate"] = int((vehicle_stats["current_passengers"] / MAX_CAPACITY) * 100)
    else:
        vehicle_stats["occupancy_rate"] = 0
        
    return render_template('index.html', data=vehicle_stats)


# --- ANLIK VERİ GÜNCELLEME ROTASI (AJAX İÇİN) ---
@app.route('/api/data')
def get_data():
    # Dinamiğe geçtiğinizde burası Raspberry Pi (MQTT) veya Veritabanından veri çekecek.
    # Şimdilik anlık değişimi görmek için simülasyon yapıyoruz:
    vehicle_stats["current_passengers"] += random.choice([-1, 0, 1])
    
    # Yolcu sayısı 0'ın altına düşmesin ve Max Kapasiteyi aşmasın
    if vehicle_stats["current_passengers"] < 0: 
        vehicle_stats["current_passengers"] = 0
    if vehicle_stats["current_passengers"] > MAX_CAPACITY: 
        vehicle_stats["current_passengers"] = MAX_CAPACITY
    
    # Doluluk yüzdesini güncelle
    if MAX_CAPACITY > 0:
        vehicle_stats["occupancy_rate"] = int((vehicle_stats["current_passengers"] / MAX_CAPACITY) * 100)
    
    # Frontend'e güncel veriyi gönder
    return jsonify(vehicle_stats)


# --- CANLI VİDEO AKIŞI (KAMERA) ROTASI ---
def generate_frames():
    """
    Gerçek projede burada OpenCV kameranız olacak.
    Örnek:
    import cv2
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success: break
        # YOLOv8 işlemleri...
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    """
    # Kamera bağlanana kadar sistemin çökmemesi için boş döngü (Simülasyon)
    while True:
        time.sleep(1) 
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """HTML'deki <img src="{{ url_for('video_feed') }}"> etiketinin beklediği rota"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # host='0.0.0.0' sayesinde aynı Wi-Fi ağındaki telefonunuzdan da girebilirsiniz.
    app.run(debug=True, host='0.0.0.0', port=5000)