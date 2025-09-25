from django.db import models
class DeviceToken(models.Model):
    token = models.CharField(max_length=256, unique=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
from django.db import models

class SensorData(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    gas = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default="LAYAK")
    jenis_buah = models.CharField(max_length=50, default="UNKNOWN")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.temperature}°C - {self.humidity}% - {self.status} - {self.jenis_buah}"
