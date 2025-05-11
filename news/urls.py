from django.urls import path
from .views import get_news

urlpatterns = [
    path('', get_news, name='news'),
]