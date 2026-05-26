from django.db import models

class Car(models.Model):
    brand = models.CharField(max_length=100, verbose_name="Марка автомобиля")
    plate = models.CharField(max_length=20, verbose_name="Гос. номер")
    year = models.IntegerField(verbose_name="Год выпуска")
    fuel_rate = models.FloatField(verbose_name="Норма расхода (л/км)")

    def __str__(self):
        return f"{self.brand} ({self.plate})"

class Driver(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО водителя")
    cars = models.ManyToManyField(Car, verbose_name="Автомобили", blank=True)

    def __str__(self):
        return self.name

class Trip(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name="Водитель")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    departure_time = models.DateTimeField(verbose_name="Время выезда")
    return_time = models.DateTimeField(verbose_name="Время заезда")
    start_mileage = models.FloatField(verbose_name="Начальный километраж")
    end_mileage = models.FloatField(verbose_name="Конечный километраж")

    @property
    def distance(self):
        return self.end_mileage - self.start_mileage

    @property
    def fuel_used(self):
        return self.distance * self.car.fuel_rate

    def __str__(self):
        return f"{self.driver} - {self.car} ({self.distance} км)"