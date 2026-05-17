from django.urls import path, include
from . import views
from staff import views as staff_views
from core import views as core_views

app_name = 'liveline'

urlpatterns = [
    path('', core_views.dashboard, name='dashboard_root'),
    path('queue/', views.queue, name='queue'),
    path('queue/<int:pk>/status/', views.queue_status_toggle, name='queue_status'),
    path('schedule/', staff_views.schedule, name='schedule'),
    path('clients/', staff_views.clients_list, name='clients'),
    path('services/', staff_views.services_management, name='services'),
]
