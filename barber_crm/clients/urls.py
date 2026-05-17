from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.my_appointments, name='me'),
    path('loyalty/', views.my_loyalty, name='loyalty'),
    path('loyalty/more/', views.loyalty_more, name='loyalty_more'),
]
