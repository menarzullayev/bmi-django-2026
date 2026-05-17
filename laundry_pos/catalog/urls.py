from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('cloth-types/', views.cloth_types, name='cloth_types'),
    path('service-types/', views.service_types, name='service_types'),
]
