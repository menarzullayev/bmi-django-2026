from django.urls import path
from . import views_tickets

app_name = 'tickets'

urlpatterns = [
    path('', views_tickets.ticket_list, name='list'),
    path('<int:pk>/', views_tickets.ticket_detail, name='detail'),
    path('<int:pk>/receipt/', views_tickets.ticket_receipt, name='receipt'),
    path('<int:pk>/receipt/pdf/', views_tickets.ticket_receipt_pdf, name='receipt_pdf'),
    path('<int:pk>/status/', views_tickets.ticket_status_change, name='status'),
    path('<int:pk>/pay/', views_tickets.ticket_pay, name='pay'),
    path('by-number/<str:ticket_number>/', views_tickets.ticket_by_number, name='by_number'),
]
