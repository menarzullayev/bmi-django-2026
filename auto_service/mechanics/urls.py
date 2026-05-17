from django.urls import path

from . import views


urlpatterns = [
    path('', views.mechanic_list, name='list'),
    path('<int:pk>/', views.mechanic_detail, name='detail'),
]
