from django.urls import path

from . import views


urlpatterns = [
    path('', views.part_list, name='list'),
    path('new/', views.part_new, name='new'),
    path('<int:pk>/', views.part_detail, name='detail'),
    path('<int:pk>/adjust/', views.part_adjust, name='adjust'),
]
