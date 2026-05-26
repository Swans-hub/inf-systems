from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('', views.salary_report, name='salary_report'),
]