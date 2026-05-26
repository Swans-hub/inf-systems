from django.shortcuts import render
from .models import Driver, Car, Trip


def fleet_report(request):
    # Данные по водителям (пробег)
    drivers_data = []
    for driver in Driver.objects.all():
        total_distance = sum(t.distance for t in Trip.objects.filter(driver=driver))
        drivers_data.append({'name': driver.name, 'distance': total_distance})  # было full_name → стало name

    # Средний пробег
    avg_distance = sum(d['distance'] for d in drivers_data) / len(drivers_data) if drivers_data else 0

    # Данные по автомобилям (расход топлива)
    cars_data = []
    for car in Car.objects.all():
        total_fuel = sum(t.fuel_used for t in Trip.objects.filter(car=car))
        cars_data.append({'name': f"{car.brand} ({car.plate})", 'fuel': total_fuel})

    # Средний расход
    avg_fuel = sum(c['fuel'] for c in cars_data) / len(cars_data) if cars_data else 0

    return render(request, 'fleet/report.html', {
        'drivers_data': drivers_data,
        'cars_data': cars_data,
        'avg_distance': avg_distance,
        'avg_fuel': avg_fuel,
    })