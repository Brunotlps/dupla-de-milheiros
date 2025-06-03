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
    checkout_session_id = request.session.get('checkout_session_id')
    
    if not checkout_session_id:
        messages.error(request, "Sessão de checkout inválida ou expirada")
        return redirect('products:course_list')
    
    try:
        checkout_session = CheckoutSession.objects.get(session_id=checkout_session_id)

        if checkout_session.is_expired():
            del request.session['checkout_session_id']
            messages.error(request, "Sessão de checkout inválida ou expirada")
            return redirect('products:course_list')
        
        course = checkout_session.course
        
    except CheckoutSession.DoesNotExist:
        messages.error(request, "Sessão de checkout inválida ou expirada")
        return redirect('products:course_list')


    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            checkout_session.payment_method = payment_method
            checkout_session.save()
            return redirect('products:checkout_payment')
    else:
        form = PaymentMethodForm()
    
    return render(request, 'products/checkout/payment_method.html', {
        'form': form,
        'checkout_session': checkout_session,
        'course': course
    })

@login_required
def checkout_payment(request):
    checkout_session_id = request.session.get("checkout_session_id")
    if not checkout_session_id:
        messages.error(request, "Sessão de checkout inválida ou expirada.")
        return redirect('products:course_list')
    
    # # Verificar se o método de pagamento foi selecionado
    # if not checkout_session_id.payment_method:
    #     return redirect('products:checkout_payment_method')
    
    # course = checkout_session.course
    # payment_method = checkout_session.payment_method
    
    # # Obter as configurações de pagamento ativas
    # payment_settings = PaymentSettings.get_active_settings()
    
    # if request.method == 'POST':
    #     # Formulário para informações do cliente
    #     customer_form = CustomerInfoForm(request.POST)
        
    #     # Formulário específico para o método de pagamento
    #     if payment_method == 'credit_card':
    #         payment_form = CreditCardForm(request.POST)
    #     else:
    #         # Para boleto e PIX, não precisamos de formulário adicional
    #         payment_form = forms.Form(request.POST)
        
    #     if customer_form.is_valid() and payment_form.is_valid():
    #         # Processar o pagamento (implementaremos na próxima etapa)
    #         # Por enquanto, apenas simularemos o processo
            
    #         # Criar o registro de compra
    #         purchase = Purchases.objects.create(
    #             user=request.user,
    #             course=course,
    #             value=course.price,
    #             status='pending',
    #             payment_method=payment_method,
    #             payer_email=customer_form.cleaned_data['email'],
    #             payer_document=customer_form.cleaned_data['cpf']
    #         )
            
    #         if payment_method == 'credit_card':
    #             purchase.installments = payment_form.cleaned_data['installments']
    #             purchase.save()
            
    #         # Marcar a sessão de checkout como concluída
    #         checkout_session.is_completed = True
    #         checkout_session.save()
            
    #         # Limpar a sessão de checkout
    #         if 'checkout_session_id' in request.session:
    #             del request.session['checkout_session_id']
            
    #         # Redirecionar para a página de sucesso
    #         return redirect('products:checkout_success', purchase_id=purchase.id)
    # else:
    #     # Pré-preencher o email se o usuário tiver um
    #     initial_data = {}
    #     if request.user.email:
    #         initial_data['email'] = request.user.email
    #     if hasattr(request.user, 'first_name') and hasattr(request.user, 'last_name'):
    #         if request.user.first_name or request.user.last_name:
    #             initial_data['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        
    #     customer_form = CustomerInfoForm(initial=initial_data)

    #     if payment_method == 'credit_card':
    #         payment_form = CreditCardForm()
    #     else:
    #         payment_form = None
    
    # return render(request, 'products/checkout/payment.html', {
    #     'customer_form': customer_form,
    #     'payment_form': payment_form,
    #     'course': course,
    #     'checkout_session': checkout_session,
    #     'payment_method': payment_method,
    #     'payment_settings': payment_settings
    # })

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



"""
        Explique a funcionalidade dos seguintes trechos de código:

card_number = self.cleaned_data.get('card_number')


def clean_expiry_date(self):
        Valida o formato da data de validade
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date:
            # Remover barras e espaços
"""