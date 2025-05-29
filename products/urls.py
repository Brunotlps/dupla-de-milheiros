from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('cursos/', views.course_list, name='course_list'),
    path('cursos/<slug:slug>/', views.course_detail, name='course_detail'),
    path('checkout/<slug:course_slug>/', views.checkout_start, name='checkout_start'),
    path('checkout/payment-method/', views.checkout_payment_method, name='checkout_payment_method'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout/success/<int:purchase_id>/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/<int:purchase_id>/', views.purchase_detail, name='purchase_detail'),
]
