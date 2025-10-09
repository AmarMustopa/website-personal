# ==========================================================
# Landing Auth View
# ==========================================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
def landing_auth(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing_auth.html')
import os
import csv
import pickle
import numpy as np
import json
import requests
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SensorData, DeviceToken
from .serializers import SensorDataSerializer


# ==========================================================
# 🔔 Register Device Token
# ==========================================================
@api_view(['POST'])
def register_token(request):
    token = request.data.get('token')
    if token:
        DeviceToken.objects.update_or_create(token=token)
        print(f"DEBUG: Token device baru diregister = {token}")
        return Response({'status': 'ok'})
    print("WARNING: Tidak ada token di request")
    return Response({'status': 'error', 'message': 'No token'}, status=400)


# ==========================================================
# 🔔 Kirim Notifikasi FCM
# ==========================================================
def send_fcm_notification(token, title, body):
    server_key = "YOUR_FCM_SERVER_KEY"  # ganti dengan server key FCM Anda
    url = "https://fcm.googleapis.com/fcm/send"
    headers = {
        "Authorization": "key=" + server_key,
        "Content-Type": "application/json"
    }
    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body
        }
    }
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"DEBUG: FCM response = {r.status_code}, {r.text}")
    except Exception as e:
        print("ERROR: Gagal kirim FCM:", e)


# ==========================================================
# 📊 Export Data ke CSV
# ==========================================================
def export_csv(request):
    qs = SensorData.objects.all()
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    status = request.GET.get('status')
    if date_str:
        qs = qs.filter(created_at__date=date_str)
    if time_str:
        qs = qs.filter(created_at__time=time_str)
    if status:
        qs = qs.filter(status=status)
    print(f"DEBUG: Export {qs.count()} data ke CSV (filter: date={date_str}, time={time_str}, status={status})")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sensor_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Waktu', 'Suhu', 'Kelembapan', 'Gas', 'Status'])
    for row in qs.order_by('-created_at'):
        writer.writerow([row.created_at, row.temperature, row.humidity, row.gas, row.status])
    return response


# ==========================================================
# 📊 Dashboard View
# ==========================================================
@login_required
def dashboard(request):
    latest = SensorData.objects.last()
    history = SensorData.objects.all().order_by('-created_at')[:10]

    if latest:
        print(f"DEBUG: Data terbaru = {latest}")
    else:
        print("WARNING: Belum ada data sensor di DB")

    if history:
        labels = json.dumps([row.created_at.strftime('%H:%M:%S') for row in reversed(history)])
        suhu = json.dumps([row.temperature if row.temperature is not None else None for row in reversed(history)])
        hum = json.dumps([row.humidity if row.humidity is not None else None for row in reversed(history)])
    else:
        labels = '[]'
        suhu = '[]'
        hum = '[]'

    return render(request, "dashboard_test.html", {
        "data": latest,
        "history": history,
        "labels_js": labels,
        "suhu_js": suhu,
        "hum_js": hum
    })


# ==========================================================
# 🤖 AI Model Loader
# ==========================================================
def load_model():
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "fruit_quality_model.pkl")
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("DEBUG: Model AI berhasil diload")
        return model
    except FileNotFoundError:
        print("WARNING: Model AI tidak ditemukan")
        return None
    except Exception as e:
        print("ERROR: Gagal load model AI:", e)
        return None


# ==========================================================
# 📡 API untuk Update Sensor
# ==========================================================
@api_view(['POST'])
def update_sensor(request):
    temperature = request.data.get("temperature")
    humidity = request.data.get("humidity")
    gas = request.data.get("gas", 0)

    print(f"DEBUG: Data sensor masuk => Suhu={temperature}, Hum={humidity}, Gas={gas}")

    features = np.array([[temperature, humidity, gas]])
    model = load_model()

    jenis_buah = "UNKNOWN"
    status = "UNKNOWN"

    if model:
        try:
            result = model.predict(features)
            print("DEBUG: Hasil prediksi model =", result)

            if isinstance(result[0], (list, tuple)) and len(result[0]) == 2:
                status_pred, jenis_pred = result[0]
                status = "LAYAK" if status_pred == 0 else "TIDAK LAYAK"
                jenis_buah = str(jenis_pred)
            else:
                status = "LAYAK" if result[0] == 0 else "TIDAK LAYAK"
        except Exception as e:
            print("ERROR: Gagal prediksi model AI:", e)

    data = SensorData.objects.create(
        temperature=temperature,
        humidity=humidity,
        gas=gas,
        status=status,
        jenis_buah=jenis_buah
    )

    print(f"DEBUG: Data sensor tersimpan => ID={data.id}, Status={status}")

    # Broadcast notifikasi kalau TIDAK LAYAK
    if status == "TIDAK LAYAK":
        tokens = DeviceToken.objects.values_list('token', flat=True)
        for device_token in tokens:
            send_fcm_notification(
                device_token,
                "Peringatan Kualitas Buah",
                f"Status buah TIDAK LAYAK! Suhu: {temperature}°C, Kelembapan: {humidity}%"
            )

    serializer = SensorDataSerializer(data)
    return Response(serializer.data)


# ==========================================================
# 📡 API untuk ambil status terakhir
# ==========================================================
@api_view(['GET'])
def get_status(request):
    latest = SensorData.objects.last()
    if latest:
        print("DEBUG: Ambil status terakhir =", latest)
        serializer = SensorDataSerializer(latest)
        return Response(serializer.data)
    print("WARNING: Tidak ada data sensor di DB")
    return Response({"status": "error", "message": "No data"}, status=404)


# ==========================================================
# 📡 API untuk ambil riwayat
# ==========================================================
@api_view(['GET'])
def get_history(request):
    qs = SensorData.objects.all()
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    status = request.GET.get('status')
    if date_str:
        qs = qs.filter(created_at__date=date_str)
    if time_str:
        qs = qs.filter(created_at__time=time_str)
    if status:
        qs = qs.filter(status=status)
    history = qs.order_by('-created_at')[:50]
    print(f"DEBUG: Ambil history (filter: date={date_str}, time={time_str}, status={status}), total={history.count()}")
    serializer = SensorDataSerializer(history, many=True)
    return Response(serializer.data)
