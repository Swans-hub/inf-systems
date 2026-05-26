from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО сотрудника")

    def __str__(self):
        return self.name

class MoneyGiven(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата выдачи")
    purpose = models.CharField(max_length=300, blank=True, verbose_name="Назначение")

    def __str__(self):
        return f"{self.employee} — {self.amount} руб. ({self.date})"