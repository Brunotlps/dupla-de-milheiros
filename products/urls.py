# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('cursos/', views.course_list, name='course_list'),
    path('cursos/<slug:slug>/', views.course_detail, name='course_detail'),
    
    # URLs de Checkout
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/success/<int:purchase_id>/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('checkout/<slug:course_slug>/', views.checkout_start, name='checkout_start'), # Movido para depois das URLs mais específicas
    
    # URLs de Compras
    # path('purchases/', views.purchase_list, name='purchase_list'), # Comentado pois a view pode não existir
    path('purchases/<int:purchase_id>/', views.purchase_detail, name='purchase_detail'),
]
