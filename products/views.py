from django.shortcuts import get_object_or_404, render, redirect

from core import forms
from .models import Course, Module, Lesson, Purchases, CheckoutSession, PaymentSettings
from .forms import PaymentMethodForm, CreditCardForm, CustomerInfoForm
from .utils import get_mercadopago_public_key, get_mercadopago_sdk, validate_mp_signature

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page
import logging
import json


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST



logger = logging.getLogger(__name__)


@cache_page(60 * 15) 
def course_list(request):
    cache_key = 'active_courses'
    courses = cache.get(cache_key)

    if not courses:
        courses = Course.objects.filter(active=True).select_related()
        cache.set(cache_key, courses, 300)
    return render(request, 'products/course_list.html', {
        'courses':courses,
        'section': 'products'
    })

def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.prefetch_related('modules__lessons__materials'),
        slug=slug,
        active=True
    )
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
        logger.error(f"Erro ao obter Public Key: {e}")  
        return render(request, 'error.html',{'message': 'Erro na configuração de pagamento'})

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
    logger.info("Processamento de pagamento iniciado", extra={
        'user_id': request.user.id,
        'session_id': request.session.get('checkout_session_id'),
        'ip_address': request.META.get('REMOTE_ADDR')
    })

    try:
        # Recuperando os dados do Payment Brick
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f'Payload recebido no checkout_process_payment: {data}')
        form_data = data.get('formData')
        logger.info(f'formData recebido: {form_data}')

        if not form_data:
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
        payment_method_id = form_data.get('payment_method_id')

        mp_payment_data = {
            "transaction_amount": float(course.price),
            "description": f"Curso: {course.title}",
            "payment_method_id": payment_method_id,
            "payer": {
                "email": form_data.get("payer", {}).get("email"),
                "identification": {
                    "type": form_data.get("payer", {}).get("identification", {}).get("type", "CPF"),
                    "number": form_data.get("payer", {}).get("identification", {}).get("number")
                },
                "first_name": form_data.get("payer", {}).get("first_name", ""),
            },
        }
        
        # Verificando campos obrigatórios
        if not form_data.get('payment_method_id'):
            return JsonResponse({'error': 'Método de pagamento é obrigatório'}, status=400)
        
        CREDIT_CARD_METHODS = ['master', 'visa', 'amex', 'elo', 'diners', 'hipercard', 'discover', 'jcb', 'aura', 'naranja', 'cabal', 'tarshop', 'argencard']


        if payment_method_id in CREDIT_CARD_METHODS:
            logger.info("Entrou no bloco de cartão de crédito")
            if not form_data.get('token'):
                logger.warning(f"Token ausente ou inválido: {form_data.get('token')}")
                return JsonResponse({'error': 'Token do cartão de crédito é obrigatório'}, status=400)
            if form_data.get('installments') in [None, '', 0]:
                logger.warning(f"Installments ausente ou inválido: {form_data.get('installments')}")
                return JsonResponse({'error': 'Número de parcelas é obrigatório'}, status=400)
            if not form_data.get('issuer_id'):
                logger.warning(f"Issuer_id ausente ou inválido: {form_data.get('issuer_id')}")
                return JsonResponse({'error': 'ID do emissor é obrigatório'}, status=400)
            payer = form_data.get('payer', {})
            if not payer.get('email'):
                logger.warning("Payer.email ausente")
                return JsonResponse({'error': "Campo 'payer.email' obrigatório."}, status=400)
            identification = payer.get('identification', {})
            if not identification.get('number'):
                logger.warning("Payer.identification.number ausente")
                return JsonResponse({'error': "Campo 'payer.identification.number' obrigatório."}, status=400)
            
        elif payment_method_id == 'pix':
            payer = form_data.get('payer', {})
            if not payer.get('email'):
                return JsonResponse({'error': "Campo 'payer.email' obrigatório."}, status=400)
            identification = payer.get('identification', {})
            if not identification.get('number'):
                return JsonResponse({'error': "Campo 'payer.identification.number' obrigatório."}, status=400)
                
        elif payment_method_id == 'bolbradesco':
            # Verificando se o pagador tem CPF ou CNPJ
            payer = form_data.get('payer', {})
            if not payer.get('email'):
                return JsonResponse({'error': "Campo 'payer.email' obrigatório."}, status=400)

            identification = payer.get('identification', {})
            if not identification.get('number'):
                return JsonResponse({'error': "Campo 'payer.identification.number' obrigatório."}, status=400)
        
        else:
            return JsonResponse({'error': 'Método de pagamento não suportado'}, status=400)

        if payment_method_id in CREDIT_CARD_METHODS:
            mp_payment_data['token'] = form_data.get('token')
            mp_payment_data['installments'] = int(form_data.get('installments', 1))
            mp_payment_data['issuer_id'] = form_data.get('issuer_id')
        elif payment_method_id == 'pix':
            pass
        elif payment_method_id == 'bolbradesco':
            from datetime import datetime, timedelta
            # Configurando dados específicos para Boleto Bancário
            mp_payment_data["date_of_expiration"] = (datetime.now() + timedelta(days=3)).isoformat()
            if form_data.get('payer_document'):
                mp_payment_data["payer"]["identification"] = {
                    "type": "CPF",
                    "number": form_data.get('payer_document')
                }         
            else:
                return  JsonResponse({'error': "Campo 'payer_document' obrigatório."}, status=400)
        
        # Criando o pagamento no Mercado Pago
        logger.info(f"Processando pagamento para o curso {course.title} com método {mp_payment_data.get('payment_method_id')}")
        logger.info(f"Dados do pagamento: {mp_payment_data}")
        logger.info(f"Dados do pagador: {mp_payment_data.get('payer', {})}")   

        payment_response = sdk.payment().create(mp_payment_data)

        logger.info(f"Resposta do pagamento: {payment_response}")

        # Processando a resposta do pagamento
        if payment_response['status'] == 201:
            mp_payment_data = payment_response["response"]
            
            # Criando ou atualizando o registro de compra
            purchase, created = Purchases.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={
                    'status': 'pending',
                    'payment_method': mp_payment_data.get('payment_method_id'),
                    'transaction_code': mp_payment_data.get('id'),
                    'value': mp_payment_data.get('transaction_amount'),
                    'payer_email': mp_payment_data['payer'].get('email'),
                    'payer_document': mp_payment_data['payer']['identification'].get('number'),
                    'gateway_response': mp_payment_data
                }
            )

            # Atualizando o status da compra
            payment_status = mp_payment_data.get("status")
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
            purchase.transaction_code = mp_payment_data.get('id')
            purchase.installments = mp_payment_data.get('installments', 1)
            purchase.payment_url = mp_payment_data.get('transaction_details', {}).get('external_resource_url')
            purchase.payment_expiration = mp_payment_data.get('transaction_details', {}).get('expiration_date')
            purchase.gateway_response = mp_payment_data    

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
                    'error_details': mp_payment_data.get('status_detail', 'Erro desconhecido')
                }, status=400)
        else:
            # Tratamento de erros 
            error_status = payment_response.get("status", 0)
            error_message = payment_response.get("response", {}). get("message", "Erro desconhecido")
            logger.error(f"Erro ao processar pagamento: {error_message} (Status: {error_status})")

            if error_status == 400:
                return JsonResponse({
                    'status': 'error',
                    'message': "Dados de pagamento inválidos.",
                    'error_details': error_message
                }, status=400)
            elif error_status == 401:
                # Erro de autenticação (credencias inválidas)
                return JsonResponse({
                    'status': 'error',
                    'message': "Erro de autenticação com o gateway de pagamento, verurifique as credenciais.",
                    'error_details': error_message
                }, status=500)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': "Erro ao processar o pagamento.",
                    'error_details': error_message
                }, status=500)
            

    except Exception as e:
        logger.error(f"Erro ao processar pagamento: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': "Erro interno ao processar o pagamento.",
            'error_details': str(e)
        }, status=500)


@csrf_exempt
def webhook_mp(request):
    

    client_ip = request.META.get('REMOTE_ADDR')
    cache_key = f'webhook_rate_limit_{client_ip}'

    if cache.get(cache_key):
        logger.warning(f"Taxa de requisições excedida para o IP: {client_ip}")
        return JsonResponse({'error': 'Taxa de requisições excedida. Tente novamente mais tarde.'}, status=429)
    
    cache.set(cache_key, True, 60)
    
    signature = request.headers.get('X-signature')
    if not validate_mp_signature(signature, request.body):
        return HttpResponseForbidden()

    if request.method != 'POST':
        logger.warning("Webhook recebido com método diferente de POST.")
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        logger.error("Webhook recebido com JSON inválido.")
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    logger.info(f"Webhook recebido: {data}")

    if data.get('type') != 'payment':
        return JsonResponse({'status': 'ignored'}, status=200)

    payload = data.get('data', {})
    if not payload:
        logger.warning("Webhook recebido sem payload de dados.")
        return JsonResponse({'error': 'Payload de dados ausente'}, status=400)

    payment_id = payload.get('id')
    if not payment_id:
        logger.error("Webhook recebido sem ID de pagamento.")
        return JsonResponse({'error': 'ID de pagamento ausente'}, status=400)

    sdk = get_mercadopago_sdk()
    try:
        payment_info = sdk.payment().get(payment_id)
    except Exception as e:
        logger.error(f"Erro ao recuperar informações do pagamento: {str(e)}")
        return JsonResponse({'error': 'Erro ao recuperar informações do pagamento'}, status=500)

    if payment_info.get('status') != 200:
        logger.error(f"Erro ao recuperar informações do pagamento: {payment_info.get('message', 'Erro desconhecido')}")
        return JsonResponse({'error': 'Erro ao recuperar informações do pagamento'}, status=400)

    payment_data = payment_info['response']
    transaction_code = payment_data.get('id')
    payment_status = payment_data.get('status')

    # Mapeamento correto dos status
    status_map = {
        'approved': 'approved',
        'pending': 'pending',
        'rejected': 'rejected',
        'canceled': 'canceled',
        'refunded': 'refunded',
        'in_process': 'in_process',
        'charged_back': 'charged_back',
        'in_mediation': 'in_mediation',
    }
    new_status = status_map.get(payment_status)

    try:
        purchase = Purchases.objects.get(transaction_code=str(payment_id))
    except Purchases.DoesNotExist:
        logger.error(f"Compra não encontrada para o ID de transação: {transaction_code}")
        return JsonResponse({'error': 'Compra não encontrada'}, status=404)

    if new_status and purchase.status != new_status:
        old_status = purchase.status
        purchase.status = new_status
        purchase.save()
        logger.info(f"Compra {purchase.id} atualizada de {old_status} para {purchase.status}")
    else:
        logger.info(f"Compra {purchase.id} já está no status: {purchase.status}, nenhuma atualização necessária.")

    return JsonResponse({'status': 'success', 'message': 'Pagamento processado com sucesso'}, status=200)
    

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

    return render(request, 'products/purchases/detail.html', {
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



