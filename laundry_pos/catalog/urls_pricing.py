from django.urls import path
from . import views

app_name = 'pricing'

urlpatterns = [
    path('', views.pricing_matrix, name='matrix'),
    path('cell/<int:cloth_id>/<int:service_id>/', views.price_cell, name='cell'),
    path('cell/<int:cloth_id>/<int:service_id>/edit/', views.price_cell_edit, name='cell_edit'),
    path('cell/<int:cloth_id>/<int:service_id>/save/', views.price_cell_save, name='cell_save'),
]
