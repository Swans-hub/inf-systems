from django.db import models


class Employee(models.Model):
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    position = models.CharField(max_length=100, verbose_name="Должность")
    address = models.TextField(verbose_name="Адрес")
    work_phone = models.CharField(max_length=20, verbose_name="Рабочий телефон")
    personal_phone = models.CharField(max_length=20, verbose_name="Личный телефон")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"