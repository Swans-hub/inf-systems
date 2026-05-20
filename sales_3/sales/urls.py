from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Управление структурой
    path('fields/', views.field_list, name='field_list'),
    path('fields/add/', views.field_add, name='field_add'),
    path('fields/edit/<int:pk>/', views.field_edit, name='field_edit'),
    path('fields/delete/<int:pk>/', views.field_delete, name='field_delete'),

    # Управление данными
    path('records/', views.record_list, name='record_list'),
    path('records/add/', views.record_add, name='record_add'),
    path('records/edit/<int:pk>/', views.record_edit, name='record_edit'),
    path('records/delete/<int:pk>/', views.record_delete, name='record_delete'),

    # Расчёт и экспорт
    path('profit/', views.profit_report, name='profit_report'),
    path('export/', views.export_excel, name='export_excel'),
]