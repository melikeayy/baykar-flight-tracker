from django.db import models
from django.utils import timezone

class Plane(models.Model):
    name = models.CharField(max_length=100)  # Uçağın adı
    flight_number = models.CharField(max_length=20, unique=True, default="FL000")  # Uçuş numarası
    latitude = models.FloatField()  # Enlem
    longitude = models.FloatField()  # Boylam
    altitude = models.FloatField()  # Yükseklik
    speed = models.FloatField()  # Hız 
    heading = models.FloatField(default=0)  # Yön (0-360 derece)
    trail = models.JSONField(default=list)  # Uçağın geçtiği yerleri liste olarak tutacağız.
    description = models.TextField(blank=True)  # Uçak hakkında açıklama 
    last_updated = models.DateTimeField(auto_now=True)  # Son güncelleme zamanı
    is_active = models.BooleanField(default=True)  # Aktif uçuş mu?

    def to_geojson_feature(self):
        """Frontend için GeoJSON formatında döndür"""
        return {
            "type": "Feature",
            "properties": {
                "id": self.id,
                "name": self.name,
                "flight_number": self.flight_number,
                "altitude": self.altitude,
                "speed": self.speed,
                "heading": self.heading,
                "description": self.description,
                "is_active": self.is_active,
                "last_updated": self.last_updated.isoformat() if self.last_updated else None
            },
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude]  # [boylam, enlem] sırası önemli!
            }
        }

    def add_to_trail(self, max_trail_length=50):
        """Mevcut konumu trail'e ekle"""
        current_position = [self.longitude, self.latitude]
        if not self.trail:
            self.trail = []
        
        # Aynı konumu tekrar ekleme
        if self.trail and len(self.trail) > 0 and self.trail[-1] == current_position:
            return
            
        self.trail.append(current_position)
        
        # Trail uzunluğunu sınırla (performans için)
        if len(self.trail) > max_trail_length:
            self.trail = self.trail[-max_trail_length:]
        
        self.save()

    def __str__(self):
        return f"{self.name} ({self.flight_number})"

    class Meta:
        ordering = ['-last_updated']
        verbose_name = "Plane"
        verbose_name_plural = "Planes"
   