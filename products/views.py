from django.shortcuts import get_object_or_404, render, redirect

from core import forms
from .models import Course, Module, Lesson, Purchases, CheckoutSession, PaymentSettings
from .forms import PaymentMethodForm, CreditCardForm, CustomerInfoForm
from .utils import get_mercadopago_public_key

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
import logging


logger = logging.getLogger(__name__)



def course_list(request):
    courses = Course.objects.filter(active=True)
    return render(request, 'products/course_list.html', {
        'courses':courses,
        'section': 'products'
    })

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, active=True)
    modules = course.modules.all().order_by('order')

    user_purchased = False
    if request.user.is_authenticated:
        user_purchased = course.purchases.filter(user=request.user, status='approved').exists()

    return render(request, 'products/course_detail.html', {
        'course': course,
        'modules': modules,
        'user_purchased': user_purchased,
        'section': 'products'
    })

@login_required
def checkout_start(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, active=True)

    if Purchases.objects.filter(user=request.user, course=course, status='approved'). exists():
        messages.info(request, "Você já adquiriu este produto")
        return redirect('products:course_detail', slug=course_slug)
    
    checkout_session, created = CheckoutSession.objects.get_or_create(
        user=request.user,
        course=course,
        is_completed=False,
        defaults={
            'expires_at': timezone.now() + timezone.timedelta(minutes=30)
        }
    )

    if not created and checkout_session.is_expired():
        checkout_session.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        checkout_session.save()
    
    request.session['checkout_session_id'] = checkout_session.session_id

    logger.info(f"Usuário {request.user.username} iniciou o checkout para o curso {course.slug}")
    logger.info(f"Checkout Session ID: {request.session.get('checkout_session_id')}")
    return redirect('products:checkout_payment')

@login_required
def checkout_payment(request,):
    checkout_session_id = request.session.get("checkout_session_id")
    if not checkout_session_id:
        messages.error(request, "Sessão de checkout inválida ou expirada.")
        return redirect('products:course_list')

    try:
        checkout_session = CheckoutSession.objects.select_related('course').get(session_id=checkout_session_id)
        if checkout_session.is_expired():
            del request.session["checkout_session_id"]
            return redirect("products:course_list")
        
        course = checkout_session.course
        public_key = get_mercadopago_public_key()
    
    except CheckoutSession.DoesNotExist:
        return redirect("products:course_list") 
    
    except ValueError as e:
        print(f"Erro ao obter Public Key: {e}")
        return render(request, 'error_page.html',{'message': 'Erro na configuração de pagamento'})

    if request.method == "POST":
        pass

    context = {
        'checkout_session': checkout_session,
        'course': course,
        'mercadopago_public_key': public_key,
        'payment_amount': course.price
    }

    logger.info(f"Renderizando template de pagamento para o curso {course.title}")
    
    return render(request, "products/checkout/payment.html", context)

@login_required
def checkout_success(request, purchase_id):
     purchase = get_object_or_404(Purchases, id=purchase_id, user=request.user)
     return render(request, 'products/checkout/success.html', {
         'purchase': purchase,
     })


@login_required
def checkout_cancel(request):
    checkout_session_id = request.session.get('checkout_session_id')
    if checkout_session_id:
        try:
            checkout_session = CheckoutSession.objects.get(
                session_id=checkout_session_id,
                user=request.user
            )

            checkout_session.delete()

            del request.session['checkout_session_id']

            messages.info(request, "Checkout cancelado com sucesso")
        except CheckoutSession.DoesNotExist:
            pass
    return redirect('products:course_list')



@login_required
def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(Purchases, id=purchase_id, user=request.user)

    return render(request, '/products/purchases/detail.html', {
        'purchase': purchase
    })

# Função auxiliar para recuperar a sessão de checkout
def get_checkout_session(request):
    # recupera a sessão a partir da sessão do django
    checkout_session_id = request.session.get('checkout_session_id')
    if not checkout_session_id:
        return None
    
    try:
        checkout_session = CheckoutSession.objects.get(
            session_id=checkout_session_id,
            user=request.user,
            is_completed=False
        )

        if checkout_session.is_expired():
            return None
        
        return checkout_session
    except CheckoutSession.DoesNotExist:
        return None



