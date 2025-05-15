from django.contrib import admin
from django.urls import path, include
from . import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('news/', include('news.urls')),
    path('accounts/signup/', core_views.signup_view, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]
