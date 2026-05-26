from django.contrib import admin
from .models import Car, Driver, Trip

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'plate', 'year', 'fuel_rate')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_cars')
    filter_horizontal = ('cars',)

    def get_cars(self, obj):
        return ", ".join([c.brand for c in obj.cars.all()])
    get_cars.short_description = "Автомобили"

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('driver', 'car', 'departure_time', 'distance', 'fuel_used')