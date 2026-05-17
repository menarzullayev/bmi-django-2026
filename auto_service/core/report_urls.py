from django.urls import path

from . import views

urlpatterns = [
    path('', views.reports_daily, name='index'),
    path('daily/', views.reports_daily, name='daily'),
]
