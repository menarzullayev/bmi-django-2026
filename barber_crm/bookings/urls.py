from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_calendar, name='calendar'),
    path('slots/', views.booking_slots, name='slots'),
    path('confirm/<int:service_id>/<int:barber_id>/<str:datetime_str>/', views.booking_confirm, name='confirm'),
    path('success/<int:pk>/', views.booking_success, name='success'),
]
