from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО сотрудника")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class SalaryAccrual(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Начислено")
    date = models.DateField(auto_now_add=True, verbose_name="Дата начисления")

    def __str__(self):
        return f"{self.employee.name} - {self.amount} руб."

    class Meta:
        verbose_name = "Начисление зарплаты"
        verbose_name_plural = "Начисления зарплаты"
