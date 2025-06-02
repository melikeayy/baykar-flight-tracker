import random
import time
import math
from django.core.management.base import BaseCommand
from tracker.models import Plane

class Command(BaseCommand):
    help = 'Updates plane positions continuously with realistic movement'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create 10 sample planes if none exist',
        )
        parser.add_argument(
            '--recreate',
            action='store_true',
            help='Delete all existing planes and create new ones',
        )

    def handle(self, *args, **options):
        if options['recreate']:
            Plane.objects.all().delete()
            self.stdout.write('All existing planes deleted.')
            self.create_sample_planes()
            return
        
        if options['create_sample'] or Plane.objects.count() == 0:
            self.create_sample_planes()

        self.stdout.write('Starting realistic flight position updates...')
        
        try:
            while True:
                self.update_all_planes()
                time.sleep(2)  # Her 2 saniyede güncelle (daha yavaş)
        except KeyboardInterrupt:
            self.stdout.write('Stopping flight updates...')

    def create_sample_planes(self):
        sample_planes = [
            {"name": "Baykar TB2", "flight_number": "BY001", "lat": 41.0082, "lng": 28.9784, "target_lat": 41.1082, "target_lng": 29.1784},
            {"name": "Baykar TB3", "flight_number": "BY002", "lat": 41.0182, "lng": 28.9884, "target_lat": 40.8182, "target_lng": 28.7884},
            {"name": "Baykar Akıncı", "flight_number": "BY003", "lat": 40.9982, "lng": 28.9684, "target_lat": 41.2982, "target_lng": 29.2684},
            {"name": "Turkish Aerospace", "flight_number": "TA101", "lat": 41.0282, "lng": 28.9984, "target_lat": 40.7282, "target_lng": 28.6984},
            {"name": "HAVELSAN Drone", "flight_number": "HV201", "lat": 40.9882, "lng": 28.9584, "target_lat": 41.3882, "target_lng": 29.3584},
            {"name": "ASELSAN UAV", "flight_number": "AS301", "lat": 41.0382, "lng": 29.0084, "target_lat": 40.6382, "target_lng": 28.5084},
            {"name": "STM Kargu", "flight_number": "ST401", "lat": 40.9782, "lng": 28.9484, "target_lat": 41.4782, "target_lng": 29.4484},
            {"name": "ROKETSAN Missile", "flight_number": "RK501", "lat": 41.0482, "lng": 29.0184, "target_lat": 40.5482, "target_lng": 28.4184},
            {"name": "TÜBİTAK Test", "flight_number": "TB601", "lat": 40.9682, "lng": 28.9384, "target_lat": 41.5682, "target_lng": 29.5384},
            {"name": "Kale Aerospace", "flight_number": "KA701", "lat": 41.0582, "lng": 29.0284, "target_lat": 40.4582, "target_lng": 28.3284}
        ]
        
        for plane_data in sample_planes:
            if not Plane.objects.filter(flight_number=plane_data["flight_number"]).exists():
                # Başlangıç heading'ini hedef yöne göre hesapla
                initial_heading = self.calculate_heading(
                    plane_data["lat"], plane_data["lng"],
                    plane_data["target_lat"], plane_data["target_lng"]
                )
                
                Plane.objects.create(
                    name=plane_data["name"],
                    flight_number=plane_data["flight_number"],
                    latitude=plane_data["lat"] + random.uniform(-0.002, 0.002),
                    longitude=plane_data["lng"] + random.uniform(-0.002, 0.002),
                    altitude=random.randint(8000, 12000),
                    speed=random.randint(350, 450),
                    heading=initial_heading,
                    description=f"Realistic flight simulation for {plane_data['name']}"
                )
        
        self.stdout.write(f'Created {len(sample_planes)} sample planes with realistic parameters')

    def calculate_heading(self, lat1, lng1, lat2, lng2):
        """İki nokta arasındaki açıyı hesapla (0-360 derece)"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lng_diff_rad = math.radians(lng2 - lng1)
        
        y = math.sin(lng_diff_rad) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lng_diff_rad)
        
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        
        # 0-360 arası normalize et
        return (heading_deg + 360) % 360

    def calculate_distance(self, lat1, lng1, lat2, lng2):
        """İki nokta arasındaki mesafeyi km cinsinden hesapla"""
        R = 6371  # Dünya yarıçapı km
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat_rad = math.radians(lat2 - lat1)
        dlng_rad = math.radians(lng2 - lng1)
        
        a = math.sin(dlat_rad/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng_rad/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

    def update_all_planes(self):
        """Tüm uçakların pozisyonlarını gerçekçi şekilde güncelle"""
        planes = Plane.objects.filter(is_active=True)
        
        for plane in planes:
            # Trail'e mevcut pozisyonu ekle
            plane.add_to_trail()
            
            # Gerçekçi hareket hesapla
            self.realistic_movement(plane)
            
            plane.save()
        
        self.stdout.write(f'Updated {planes.count()} planes with realistic movement')

    def realistic_movement(self, plane):
        """Gerçekçi uçak hareketi simülasyonu"""
        # Hızı km/h'den derece/saniye'ye çevir (yaklaşık)
        # 1 derece ≈ 111 km, 1 saat = 3600 saniye
        speed_deg_per_sec = (plane.speed / 111) / 3600
        
        # 2 saniyede kat edilecek mesafe
        distance_per_update = speed_deg_per_sec * 2
        
        # Mevcut heading'e göre hareket
        heading_rad = math.radians(plane.heading)
        
        # Yeni pozisyon hesapla
        lat_change = distance_per_update * math.cos(heading_rad)
        lng_change = distance_per_update * math.sin(heading_rad)
        
        plane.latitude += lat_change
        plane.longitude += lng_change
        
        # Heading'de küçük değişiklikler (rüzgar, pilot müdahalesi simülasyonu)
        heading_change = random.uniform(-2, 2)  # ±2 derece
        plane.heading = (plane.heading + heading_change) % 360
        
        # Hızda küçük değişiklikler
        speed_change = random.uniform(-5, 5)
        plane.speed = max(300, min(500, plane.speed + speed_change))
        
        # Yükseklikte küçük değişiklikler
        altitude_change = random.uniform(-50, 50)
        plane.altitude = max(5000, min(15000, plane.altitude + altitude_change))
        
        # Sınır kontrolü - uçaklar çok uzaklaşmasın
        if abs(plane.latitude - 41.0) > 0.5 or abs(plane.longitude - 29.0) > 0.5:
            # Merkeze dönüş heading'i hesapla
            return_heading = self.calculate_heading(
                plane.latitude, plane.longitude,
                41.0 + random.uniform(-0.1, 0.1),
                29.0 + random.uniform(-0.1, 0.1)
            )
            plane.heading = return_heading