from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Plane  
from .serializers import PlaneSerializer  

class PlaneViewSet(viewsets.ModelViewSet):
    queryset = Plane.objects.all()
    serializer_class = PlaneSerializer

@api_view(['GET'])
def get_geojson(request):
    """Harita için GeoJSON formatında uçak verilerini döndür"""
    planes = Plane.objects.filter(is_active=True) if hasattr(Plane.objects.first(), 'is_active') else Plane.objects.all()
    
    features = []
    for plane in planes:
        if hasattr(plane, 'to_geojson_feature'):
            features.append(plane.to_geojson_feature())
        else:
        
            features.append({
                "type": "Feature",
                "properties": {
                    "id": plane.id,
                    "name": plane.name,
                    "altitude": plane.altitude,
                    "speed": plane.speed,
                    "description": getattr(plane, 'description', ''),
                    "trail": getattr(plane, 'trail', [])
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [plane.longitude, plane.latitude]
                }
            })
    
    return Response({
        "type": "FeatureCollection",
        "features": features
    })


@api_view(['GET'])
def get_plane_trail(request, plane_id):
    """Belirli bir uçağın trail verilerini döndür"""
    try:
        plane = Plane.objects.get(id=plane_id)
        return Response({
            "type": "LineString",
            "coordinates": getattr(plane, 'trail', [])
        })
    except Plane.DoesNotExist:
        return Response({"error": "Plane not found"}, status=404)
    