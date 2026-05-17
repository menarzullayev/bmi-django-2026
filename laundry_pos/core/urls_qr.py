from django.urls import path
from . import views

app_name = 'qr'

urlpatterns = [
    path('<str:ticket_number>/', views.public_status, name='public_status'),
]
