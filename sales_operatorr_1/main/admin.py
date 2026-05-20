from django.contrib import admin
from .models import Client, Product, Order, OrderItem

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_purchases', 'current_account', 'current_debt', 'credit_remaining')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity')
    search_fields = ('name',)

admin.site.register(Order)
admin.site.register(OrderItem)
