from django.urls import path

from . import views


urlpatterns = [
    path('', views.customer_list, name='list'),
    path('<int:pk>/', views.customer_detail, name='detail'),
]
