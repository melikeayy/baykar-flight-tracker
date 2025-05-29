from django.contrib import admin
from .models import Plane  

@admin.register(Plane)
class PlaneAdmin(admin.ModelAdmin):
    list_display = ['name', 'flight_number', 'latitude', 'longitude', 'altitude', 'speed', 'is_active', 'last_updated']
    list_filter = ['is_active', 'last_updated']
    search_fields = ['name', 'flight_number']
    readonly_fields = ['last_updated']
    
    fieldsets = (
        ('Flight Information', {
            'fields': ('name', 'flight_number', 'description', 'is_active')
        }),
        ('Location & Movement', {
            'fields': ('latitude', 'longitude', 'altitude', 'speed', 'heading')
        }),
        ('Trail Data', {
            'fields': ('trail',),
            'classes': ('collapse',) 
        }),
        ('System', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        })
    )
    
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} plane(s) activated.")
    make_active.short_description = "Mark selected planes as active"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} plane(s) deactivated.")
    make_inactive.short_description = "Mark selected planes as inactive"