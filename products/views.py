from django.shortcuts import get_object_or_404, render
from .models import Course, Module, Lesson

def course_list(request):
    courses = Course.objects.filter(active=True)
    return render(request, 'products/course_list.html', {'courses':courses})

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