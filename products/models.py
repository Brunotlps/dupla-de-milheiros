from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['active', '-creation_date']),
        ]

        ordering = ['-creation_date']
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Module(models.Model):
    
    
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        
        
        ordering = ['order']
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
    
    def __str__(self):
        
        
        return f'{self.title} - {self.course.title}'

class Lesson(models.Model):
    
    
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_url = models.URLField(blank=True, null=True, help_text="URL direta do vídeo (compatibilidade)")
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duração em minutos", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)


    # Sistemas de video Vimeo / Vimeo video system
    VIDEO_PROVIDER_CHOICES = [
        ('direct', 'URL Direta'),
        ('vimeo', 'Vimeo'),
        ('youtube', 'YouTube'),
    ]

    
    UPLOAD_STATUS_CHOICES = [
        ('ready', 'Pronto'),
        ('pending', 'Pendente'),
        ('uploading', 'Enviando'),
        ('processing', 'Processando'),
        ('error', 'Erro'),
    ]


    video_provider = models.CharField(
        max_length=20,
        choices=VIDEO_PROVIDER_CHOICES,
        default='direct',
        help_text="Provedor de vídeo"
    )

    vimeo_video_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="ID do vídeo no Vimeo (se aplicável)"
    )

    upload_status = models.CharField(
        max_length=20,
        choices=UPLOAD_STATUS_CHOICES,
        default='ready',
        help_text="Status do upload do vídeo"
    )

    
    class Meta:
        
        
        ordering = ['order']
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
    
    def __str__(self):
        
        
        return f'{self.title} - {self.module.title}'
    
    
    # Métodos para o sistema de vídeo / Methods for the video system
    def get_video_url(self):
        """Retorna a URL do vídeo baseada no provedor / Returns the video URL based on the provider"""
    
    
        if self.video_provider == 'vimeo' and self.vimeo_video_id:
            return f"https://player.vimeo.com/video/{self.vimeo_video_id}"
        elif self.video_provider == 'direct' and self.video_url:
            return self.video_url
        return None
    
    def is_video_ready(self):
        """Verifica se o vídeo está pronto para reprodução / Checks if the video is ready for playback"""
        
        
        return self.upload_status == 'ready'
    
    def get_provider_display_name(self):
        """Retorna o nome amigável do provedor / Returns the friendly name of the provider"""
        
        
        return dict(self.VIDEO_PROVIDER_CHOICES).get(self.video_provider, 'Desconhecido')
    
    def get_status_display_class(self):
        """Retorna classe CSS para o status do upload / Returns CSS class for the upload status"""
        
        
        status_classes = {
            'ready': 'success',
            'pending': 'warning', 
            'uploading': 'info',
            'processing': 'info',
            'error': 'danger',
        }
        return status_classes.get(self.upload_status, 'secondary')


class ComplementaryMaterial(models.Model):
    TYPE_CHOICES = (
        ('file', 'Arquivo'),
        ('link', 'Link Externo'),
    )
    
    lesson = models.ForeignKey(Lesson, related_name='materials', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TYPE_CHOICES, default='file')
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Material Complementar'
        verbose_name_plural = 'Materiais Complementares'
    
    def __str__(self):
        return f'{self.title} - {self.lesson.title}'
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.tipo == 'file' and not self.file:
            raise ValidationError('Para o tipo Arquivo, é necessário fazer upload de um arquivo.')
        elif self.tipo == 'link' and not self.link:
            raise ValidationError('Para o tipo Link Externo, é necessário fornecer um URL.')

class Comments(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='lesson_comments', on_delete=models.CASCADE)
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
    
    def __str__(self):
        return f'Comentário de {self.user.username} em {self.lesson.title}'

class Purchases(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('in_process', 'Em Processamento'),
        ('rejected', 'Rejeitado'),
        ('refunded', 'Reembolsado'),
        ('canceled', 'Cancelado'),
        ('in_mediation', 'Em Mediação'),
        ('charged_back', 'Estornado'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Cartão de Crédito'),
        ('bank_slip', 'Boleto'),
        ('pix', 'PIX'),
    )
    
    user = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='purchases', on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    transaction_code = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    installments = models.PositiveIntegerField(default=1) # numero de parcelas
    payment_url = models.URLField(blank=True, null=True) # url para boleto/PIX
    payment_expiration = models.DateTimeField(blank=True, null=True)
    payer_email = models.EmailField(blank=True, null=True)
    payer_document = models.CharField(max_length=20, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True ) # Resposta completa do gateway

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        unique_together = ('user', 'course') # User pode comprar o curso apenas uma vez
    
    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
    
    def is_approved(self):
        return self.status == 'approved'
    
    def is_pending(self):
        return self.status == 'pending'
    
    def is_rejected(self):
        return self.status == 'rejected'
    
    def is_canceled(self):
        return self.status == 'canceled'
    
    def is_in_process(self):
        return self.status == 'in_process'
    
    def is_refunded(self):
        return self.status == 'refunded'
    
    def is_in_mediation(self):
        return self.status == 'in_mediation'
    
    def is_charged_back(self):
        return self.status == 'charged_back'
    
    # Define a URL canônica para um objeto 'Purchase' específico 
    def get_absolute_url(self):
        return reverse("products:purchase_detail", args=[self.id])
    
    # Mapeia o status da compra para uma classe CSS do Bootstrap
    def get_status_display_class(self):
        status_classes = {
            'pending': 'warning',
            'approved': 'success',
            'in_process': 'info',
            'rejected': 'danger',
            'refunded': 'secondary',
            'canceled': 'secondary',
            'in_mediation': 'warning',
            'charged_back': 'danger',
        }

        return status_classes.get(self.status, 'secondary')

    def get_payment_method_display(self):
        payment_methods = dict(self.PAYMENT_METHOD_CHOICES)
        return payment_methods.get(self.payment_method, 'Método de pagamento desconhecido')

# Modelo para armazenar informações temporárias durante o processo de checkout

class CheckoutSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    session_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=Purchases.PAYMENT_METHOD_CHOICES, blank=True, null=True)
    installments = models.PositiveIntegerField(default=1)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Sessão de Checkout'
        verbose_name_plural = 'Sessões de Checkout'

    def __str__(self):
        return f'Checkout: {self.user.username} - {self.course.title}'
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    # Geração de id único para cada sessão de checkout
    def generate_session_id(self):
        import uuid
        return str(uuid.uuid4())
    
    # Sobrescreve o método save() e adiciona lógica personalizada antes de salvar o obj no database
    # Garante que toda nova sessão de checkout tenha ID único e implementa tempo para a sessão
    def save(self, *args, **kwargs):
        if not self.pk:
            self.session_id = self.generate_session_id()
            self.expires_at = timezone.now() + timezone.timedelta(minutes=30)
        super().save(*args, **kwargs)

class PaymentSettings(models.Model):
    name = models.CharField(max_length=50, default='Mercado Pago')
    is_active = models.BooleanField(default=True)
    is_sandbox = models.BooleanField(default=True, verbose_name='Ambiente de Testes')

    # Credenciais de Produção
    production_public_key = models.CharField(max_length=255, blank=True, null=True)
    production_access_token = models.CharField(max_length=255, blank=True, null=True)
    production_webhook_secret = models.CharField(max_length=255, blank=True, null=True, 
                                                help_text="Secret para validação de webhooks em produção")

    # Credenciais de Sandbox (Testes)
    sandbox_public_key = models.CharField(max_length=255, blank=True, null=True)
    sandbox_access_token = models.CharField(max_length=255, blank=True, null=True)
    sandbox_webhook_secret = models.CharField(max_length=255, blank=True, null=True,
                                             help_text="Secret para validação de webhooks em sandbox")

    creation_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuração de Pagamento'
        verbose_name_plural = 'Configurações de Pagamento'

    def __str__(self):
        environment = 'Sandbox' if self.is_sandbox else 'Produção'
        return f'{self.name} ({environment})'

    def get_public_key(self):
        #Retorna a chave pública adequada com base no ambiente
        return self.sandbox_public_key if self.is_sandbox else self.production_public_key
    
    def get_access_token(self):
        #Retorna o token adequado com base no ambiente
        return self.sandbox_access_token if self.is_sandbox else self.production_access_token
    
    # Fornece acesso às configurações ativas do gateway de pagamento ou cria uma padrão
    # Permite alternar facilmente entre ambientes de teste e produção
    @classmethod 
    def get_active_settings(cls):
        # Retorna as configurações ativas ou cria uma configuração padrão
        settings = cls.objects.filter(is_active=True).first()
        if not settings:
            settings = cls.objects.create(
                name='Mercado Pago',
                is_active = True,
                is_sandbox = True
            )
        return settings
    

    