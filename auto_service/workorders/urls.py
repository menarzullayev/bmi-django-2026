from django.urls import path

from . import views

urlpatterns = [
    path('', views.order_list, name='list'),
    path('new/', views.order_new, name='new'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('<int:pk>/transition/', views.order_transition, name='transition'),
    path('<int:pk>/tasks/add/', views.order_add_task, name='add_task'),
    path('<int:pk>/parts/add/', views.order_add_part, name='add_part'),
]
