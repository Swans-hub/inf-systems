from django.contrib import admin
from .models import Employee, MoneyGiven

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(MoneyGiven)
class MoneyGivenAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'date', 'purpose')
    list_filter = ('date', 'employee')