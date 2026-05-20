from django.urls import path
from . import views

app_name = 'counterparties'

urlpatterns = [
    path('', views.counterparty_list, name='counterparty_list'),
    path('create/', views.counterparty_create, name='counterparty_create'),
    path('<int:pk>/', views.counterparty_detail, name='counterparty_detail'),
    path('<int:pk>/edit/', views.counterparty_edit, name='counterparty_edit'),
    path('<int:pk>/delete/', views.counterparty_delete, name='counterparty_delete'),
    path('<int:pk>/check-inn/', views.check_inn_button, name='check_inn_button'),
    path('duplicates/find/', views.find_all_duplicates, name='find_duplicates'),
    path('duplicates/result/', views.duplicate_check_result, name='duplicate_check_result'),
]