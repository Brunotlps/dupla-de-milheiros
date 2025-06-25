from django.shortcuts import get_object_or_404, render, redirect

from core import forms
from .models import Course, Module, Lesson, Purchases, CheckoutSession, PaymentSettings
from .forms import PaymentMethodForm, CreditCardForm, CustomerInfoForm
from .utils import get_mercadopago_public_key, get_mercadopago_sdk

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.conf import settings
import logging
import json

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



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
def checkout_payment(request):
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

@require_POST
@login_required
def checkout_process_payment(request):
    try:
        # Recuperando os dados do Payment Brick
        data = json.loads(request.body.decode('utf-8'))
        payment_data = data.get('formData')

        if not payment_data:
            return JsonResponse({'error': 'Dados de pagamento inválidos'}, status=400)
        
        # Recuperando a sessão de checkout atual
        checkout_session_id = request.session.get('checkout_session_id')
        if not checkout_session_id:
            return JsonResponse({'error': 'Sessão de checkout inválida'}, status=400)  
        
        try:
            checkout_session = CheckoutSession.objects.select_related('course').get(
                session_id = checkout_session_id,
                user=request.user
            )

            if checkout_session.is_expired():
                del request.session['checkout_session_id']
                return JsonResponse({'error': 'Sessão de checkout inválida ou expirada'}, status=400)

        except CheckoutSession.DoesNotExist:
            return JsonResponse({'error': 'Sessão de checkout não encontrada'}, status=404)
        
        course = checkout_session.course
        # Inicializando o SDK do Mercado Pago
        sdk = get_mercadopago_sdk()

        payment_data = {
            "transaction_amount": float(course.price),
            "description": f"Curso: {course.title}",
            "installments": int(payment_data.get("installments")),
            "payment_method_id": payment_data.get("payment_method_id"),
            "payer": {
                "email": payment_data.get("payer", {}).get("email"),
                "identification": {
                    "type": payment_data.get("payer", {}).get("identification", {}).get("type", "CPF"),
                    "number": payment_data.get("payer", {}).get("identification", {}).get("number")
                },
                "first_name": payment_data.get("payer", {}).get("first_name", ""),
            },
        }

        # Adicionando dados do cartão de crédito se estiverem presentes
        if payment_data.get("payment_method_id") == 'credit_card':
            payment_data["token"] = payment_data.get("token")
            payment_data["installments"] = int(payment_data.get("installments", 1))
            payment_data["issuer_id"] = payment_data.get("issuer_id")
            payment_data["payment_method_id"] = payment_data.get("payment_method_id")


        payment_response = sdk.payment().create(payment_data)

        # Processando a resposta do pagamento
        if payment_response['status'] == 201:
            payment_data = payment_response["response"]
            
            # Criando ou atualizando o registro de compra
            purchase, created = Purchases.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'status': 'pending',
                    'payment_method': payment_data.get('payment_method_id'),
                    'transaction_id': payment_data.get('id'),
                    'amount': payment_data.get('transaction_amount'),
                    'payer_email': payment_data['payer'].get('email'),
                    'payer_document': payment_data['payer']['identification'].get('number'),
                    'gateway_response': payment_data
                }
            )

            # Atualizando o status da compra
            payment_status = payment_data.get("status")
            if payment_status == 'approved':
                purchase.status = 'approved'
                messages.success(request, "Pagamento aprovado com sucesso!")
            elif payment_status == 'pending':
                purchase.status = 'pending'
                messages.info(request, "Pagamento pendente. Verifique seu e-mail para mais detalhes.")
            elif payment_status == 'rejected':
                purchase.status = 'rejected'
                messages.error(request, "Pagamento rejeitado. Tente novamente.")
            elif payment_status == 'in_process':
                purchase.status = 'in_process'
                messages.info(request, "Pagamento em processo. Aguarde a confirmação.")
            elif payment_status == 'refunded':
                purchase.status = 'refunded'
                messages.info(request, "Pagamento reembolsado.")
            elif payment_status == 'canceled':
                purchase.status = 'canceled'
                messages.info(request, "Pagamento cancelado.")
            elif payment_status == 'charged_back':
                purchase.status = 'charged_back'
                messages.error(request, "Pagamento estornado.") 

            # Atualizando os detalhes da compra para salvar informações do pagamento
            purchase.transaction_code = payment_data.get('id')
            purchase.installments = payment_data.get('installments', 1)
            purchase.payment_url = payment_data.get('transaction_details', {}).get('external_resource_url')
            purchase.payment_expiration = payment_data.get('transaction_details', {}).get('expiration_date')
            purchase.gateway_response = payment_data    

            purchase.save()

            # Limpando a sessão de checkout de pagamentos bem sucedidos
            if payment_status in ['approved', 'pending', 'in_process']:
                checkout_session.is_completed = True
                checkout_session.save()

                del request.session['checkout_session_id']

            # Redirecionando para a página com base no status do pagamento
            if payment_status == 'approved':
                return JsonResponse({
                    'success': True,
                    'message': "Pagamento aprovado com sucesso!",
                    'redirect_url': reverse('products:checkout_success', args=[purchase.id])
                })
            
            elif payment_status == 'pending':
                return JsonResponse({
                    'status': 'pending',
                    'message': "Pagamento pendente. Aguarde a confirmação.",
                    'redirect_url': reverse('products:checkout_success', args=[purchase.id])
                })
            
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': "Pagamento rejeitado. Verifique os dados e tente novamente.",
                    'error_details': payment_data.get('status_detail', 'Erro desconhecido')
                }, status=400)
        else:
            return JsonResponse({
                'status': 'error',
                'message': "Erro ao processar o pagamento.",
                'error_details': payment_response.get("response", {}).get("message", "Erro desconhecido")
            }, status=400)
    

    except Exception as e:
        logger.error(f"Erro ao processar pagamento: {e}")
        return JsonResponse({
            'status': 'error',
            'message': "Erro interno ao processar o pagamento.",
            'error_details': str(e)
        }, status=500)







        



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



