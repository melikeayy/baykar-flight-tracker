from rest_framework import serializers
from .models import Plane  

class PlaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plane
        fields = '__all__'

    def validate_latitude(self, value):
        """Enlem kontrolü"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_longitude(self, value):
        """Boylam kontrolü"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value
    
    def validate_altitude(self, value):
        """Yükseklik kontrolü"""
        if value < 0:
            raise serializers.ValidationError("Altitude cannot be negative")
        return value

class PlaneGeoJSONSerializer(serializers.ModelSerializer):
    coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = Plane
        fields = ['id', 'name', 'altitude', 'speed', 'coordinates']
    
    def get_coordinates(self, obj):
        return [obj.longitude, obj.latitude]