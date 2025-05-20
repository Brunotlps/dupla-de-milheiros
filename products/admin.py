from django.contrib import admin
from .models import Course, Module, Lesson, ComplementaryMaterial, Comments, Purchases

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
    list_display = ['user', 'course', 'purchase_date', 'status']
    list_filter = ['status', 'purchase_date', 'course']
    search_fields = ['user__username', 'course__title', 'transaction_code']
    readonly_fields = ['purchase_date']
