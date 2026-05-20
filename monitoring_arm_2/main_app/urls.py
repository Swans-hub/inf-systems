from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_data/', views.add_data, name='add_data'),
    path('generate_plots/', views.generate_plots, name='generate_plots'),
]