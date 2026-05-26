from django.contrib import admin
from .models import Employee, SalaryAccrual

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(SalaryAccrual)
class SalaryAccrualAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'amount', 'date')
    list_filter = ('date', 'employee')
    search_fields = ('employee__name',)
