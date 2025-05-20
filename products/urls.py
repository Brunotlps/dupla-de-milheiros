from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('cursos/', views.course_list, name='course_list'),
    path('cursos/<slug:slug>/', views.course_detail, name='course_detail'),
]
