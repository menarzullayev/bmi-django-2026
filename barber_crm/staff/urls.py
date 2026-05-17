from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('schedule/', views.schedule, name='schedule'),
    path('clients/', views.clients_list, name='clients'),
    path('services/', views.services_management, name='services'),
]
