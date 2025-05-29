from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlaneViewSet, get_geojson, get_plane_trail

router = DefaultRouter()
router.register(r'planes', PlaneViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('geojson/', get_geojson, name='geojson'),  
    path('planes/<int:plane_id>/trail/', get_plane_trail, name='plane_trail'),
]