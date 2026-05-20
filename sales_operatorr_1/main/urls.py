from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search-clients/', views.search_clients, name='search_clients'),
    path('get-client/<int:client_id>/', views.get_client, name='get_client'),
    path('get-products/', views.get_products, name='get_products'),
    path('complete-order/', views.complete_order, name='complete_order'),
    path('order-report/', views.order_report, name='order_report'),
    path('check-products-warning/', views.check_products_warning, name='check_products_warning'),
]