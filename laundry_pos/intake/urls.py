from django.urls import path
from . import views

app_name = 'intake'

urlpatterns = [
    path('new/', views.intake_new, name='new'),
    path('customer/search/', views.customer_search, name='customer_search'),
    path('garment/add/', views.garment_add_row, name='garment_add'),
    path('price/', views.price_lookup, name='price_lookup'),
]
