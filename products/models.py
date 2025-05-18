from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Course(models.Model):

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    creation_date = models.DateTimeField(auto_now=True)
    update_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    

    class Meta:
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
    url_video = models.URLField()
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'

    def __str__(self):
        return f'{self.title} - {self.module.title}'  


class ComplementaryMaterial(models.Model):
    TIPO_CHOICES = (
        ('file', 'Files'),
        ('link', 'External Link'),
    )

    lesson = models.ForeignKey(Lesson, related_name='materials', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='file')
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
            raise ValidationError('Necessário fazer upload do arquivo.')
        elif self.tipo == 'link' and not self.link:
            raise ValidationError('Necessário fornecer um URL.')
        

class Comments(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='lesson_comment', on_delete=models.CASCADE)
    text = models.TextField
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creation_date']
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários' 

    def __str__(self):
        return f'Comentario de {self.user.username} em {self.lesson.title}'
    

class Purchases(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('canceled', 'Canceled'),
    )

    user = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='purchases', on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendent')
    transaction_code = models.CharField(max_length=100, blank=True, null=True)

    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        unique_together = ('user', 'course')  # Um usuário só pode comprar um curso uma vez
    
    def __str__(self):
        return f'{self.user.username} - {self.course.title}'
