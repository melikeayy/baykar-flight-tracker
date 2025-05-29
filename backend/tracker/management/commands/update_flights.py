import random
import time
from django.core.management.base import BaseCommand
from tracker.models import Plane

class Command(BaseCommand):
    help = 'Updates plane positions continuously'

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
        # Mevcut uçakları sil ve yenilerini oluştur
        if options['recreate']:
            Plane.objects.all().delete()
            self.stdout.write('All existing planes deleted.')
            self.create_sample_planes()
            return
        
        # Sample uçakları oluştur
        if options['create_sample'] or Plane.objects.count() == 0:
            self.create_sample_planes()

        self.stdout.write('Starting flight position updates...')
        
        try:
            while True:
                self.update_all_planes()
                time.sleep(0.5)  # Her 0.5 saniyede güncelle
        except KeyboardInterrupt:
            self.stdout.write('Stopping flight updates...')

    def create_sample_planes(self):
        sample_planes = [
            {"name": "Baykar TB2", "flight_number": "BY001", "lat": 41.0082, "lng": 28.9784},
            {"name": "Baykar TB3", "flight_number": "BY002", "lat": 41.0182, "lng": 28.9884},
            {"name": "Baykar Akıncı", "flight_number": "BY003", "lat": 40.9982, "lng": 28.9684},
            {"name": "Turkish Aerospace", "flight_number": "TA101", "lat": 41.0282, "lng": 28.9984},
            {"name": "HAVELSAN Drone", "flight_number": "HV201", "lat": 40.9882, "lng": 28.9584},
            {"name": "ASELSAN UAV", "flight_number": "AS301", "lat": 41.0382, "lng": 29.0084},
            {"name": "STM Kargu", "flight_number": "ST401", "lat": 40.9782, "lng": 28.9484},
            {"name": "ROKETSAN Missile", "flight_number": "RK501", "lat": 41.0482, "lng": 29.0184},
            {"name": "TÜBİTAK Test", "flight_number": "TB601", "lat": 40.9682, "lng": 28.9384},
            {"name": "Kale Aerospace", "flight_number": "KA701", "lat": 41.0582, "lng": 29.0284}
        ]
        
        for plane_data in sample_planes:
            if not Plane.objects.filter(flight_number=plane_data["flight_number"]).exists():
                Plane.objects.create(
                    name=plane_data["name"],
                    flight_number=plane_data["flight_number"],
                    latitude=plane_data["lat"] + random.uniform(-0.01, 0.01),
                    longitude=plane_data["lng"] + random.uniform(-0.01, 0.01),
                    altitude=random.randint(5000, 15000),
                    speed=random.randint(300, 500),
                    heading=random.randint(0, 360),
                    description=f"Sample flight from {plane_data['name']}"
                )
        
        self.stdout.write(f'Created {len(sample_planes)} sample planes')

    def update_all_planes(self):
        """Tüm uçakların pozisyonlarını güncelle"""
        planes = Plane.objects.filter(is_active=True)
        
        for plane in planes:
            # Rastgele hareket simülasyonu
            lat_change = random.uniform(-0.001, 0.001)
            lng_change = random.uniform(-0.001, 0.001)
            
            # Trail'e mevcut pozisyonu ekle
            plane.add_to_trail()
            
            # Yeni pozisyon
            plane.latitude += lat_change
            plane.longitude += lng_change
            
            # Hız ve yön değişimi
            plane.speed += random.uniform(-10, 10)
            plane.speed = max(200, min(600, plane.speed))  # 200-600 arası sınırla
            
            plane.heading += random.uniform(-15, 15)
            plane.heading = plane.heading % 360  # 0-360 arası tut
            
            plane.save()
        
        self.stdout.write(f'Updated {planes.count()} planes')