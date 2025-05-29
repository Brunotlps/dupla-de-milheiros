from django.shortcuts import get_object_or_404, render, redirect
from .models import Course, Module, Lesson, Purchases, CheckoutSession, PaymentSettings
from .forms import PaymentMethodForm, CreditCardForm, CustomerInfoForm

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

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

    return redirect('products:checkout_payment_method')

@login_required
def checkout_payment_method(request):
    checkout_session = get_checkout_session(request)
    
    if not checkout_session:
        messages.error(request, "Sessão de checkout inválida ou expirada")
        return redirect('products:course_list')
    
    course = checkout_session.course

    if request.method == 'POST':
        form = form.is_valid()
        checkout_session.payment_method = form.cleaned_data['payment_method']
        checkout_session.save()

        return redirect('products:checkout_payment')

    else:
        form = PaymentMethodForm()

    return render(request, 'products/checkout/payment_method.html', {
        'form': form,
        'course': course,
        'checkout_session': checkout_session
    })

@login_required
def checkout_payment(request):
    pass

