import requests
import random
import time

URL = "http://127.0.0.1:8000/api/sensor/"

for i in range(5):
    data = {
        "temperature": round(random.uniform(24, 30), 2),
        "humidity": round(random.uniform(55, 80), 2),
        "gas": round(random.uniform(0, 0.5), 2)
    }
    response = requests.post(URL, json=data)
    print(f"Kirim data ke API: {data} | Status: {response.status_code}")
    time.sleep(1)
