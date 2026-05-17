from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('', views.delivery_list, name='list'),
    path('route/new/', views.route_new, name='route_new'),
    path('route/<int:pk>/', views.route_detail, name='route_detail'),
    path('assignment/<int:pk>/deliver/', views.assignment_deliver, name='assignment_deliver'),
]
