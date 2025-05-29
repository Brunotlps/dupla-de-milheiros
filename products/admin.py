from django.contrib import admin
from .models import Course, Module, Lesson, ComplementaryMaterial, Comments, Purchases, CheckoutSession, PaymentSettings

# Inlines
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1  # números de formulários vazios a exibir

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class ComplementaryMaterialInline(admin.TabularInline):
    model = ComplementaryMaterial
    extra = 1

# ModelAdmins
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'active', 'creation_date']
    list_filter = ['active', 'creation_date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'description']
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'duration']
    list_filter = ['module__course', 'module']  # Corrigido: module__course com dois underscores
    search_fields = ['title', 'description']
    inlines = [ComplementaryMaterialInline]

@admin.register(ComplementaryMaterial)  # Registrando o modelo, não o inline
class ComplementaryMaterialAdmin(admin.ModelAdmin):  # Renomeado para evitar conflito
    list_display = ['title', 'lesson', 'tipo']  # Alterado 'tipo' para 'type' para corresponder ao modelo
    list_filter = ['tipo', 'lesson__module__course']  # Alterado 'tipo' para 'type'
    search_fields = ['title', 'description']

    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)

@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'creation_date']
    list_filter = ['lesson__module__course', 'creation_date']
    search_fields = ['text', 'user__username']
    readonly_fields = ['user', 'lesson', 'creation_date']

@admin.register(Purchases)
class PurchasesAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'value', 'status', 'payment_method', 'purchase_date']
    list_filter = ['status', 'payment_method', 'purchase_date']
    search_fields = ['user__username', 'course__title', 'transaction_code']
    readonly_fields = ['purchase_date', 'transaction_code', 'gateway_response']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'course', 'value', 'status', 'purchase_date')
        }),
        ('Detalhes do Pagamento', {
            'fields': ('payment_method', 'installments', 'transaction_code', 'payment_url', 'payment_expiration')
        }),
        ('Informações do Pagador', {
            'fields': ('payer_email', 'payer_document')
        }),
        ('Resposta do Gateway', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        })
    )

@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'creation_date', 'expires_at', 'is_completed']
    list_filter = ['is_completed', 'creation_date']
    search_fields = ['user__username', 'course__title', 'session_id']
    readonly_fields = ['session_id', 'creation_date', 'expires_at']

@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'is_sandbox', 'updated_at']
    list_filter = ['is_active', 'is_sandbox']
    fieldsets = (
        ('Configurações Gerais', {
            'fields': ('name', 'is_active', 'is_sandbox')
        }),
        ('Credenciais de Produção', {
            'fields': ('production_public_key', 'production_access_token'),
            'classes': ('collapse',)
        }),
        ('Credenciais de Sandbox', {
            'fields': ('sandbox_public_key', 'sandbox_access_token'),
            'classes': ('collapse',)
        })
    )