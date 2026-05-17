from django.urls import path

from . import views

urlpatterns = [
    path('', views.kanban, name='board'),
]
