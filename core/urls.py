from django.contrib import admin
from django.urls import path, include
from . import views as core_views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('news/', include('news.urls')),
    path('accounts/signup/', core_views.signup_view, name='signup'),
    path("accounts/login/", core_views.CustomLoginView.as_view(
        template_name="registration/login.html"
    ), name="login"),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

