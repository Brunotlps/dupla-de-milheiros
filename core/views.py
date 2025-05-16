from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):

    def dispatch(self, request, *args, **kwargs):
        
        if request.user.is_authenticated:
            messages.info(request, "Você já está conectado.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


def signup_view(request):

    if request.user.is_authenticated:
        messages.info(request, "Você já possui uma conta!")
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request, 'Sua conta foi cadastrada com sucesso!')
            return redirect('home')
        else:
            messages.error(request, "Não foi possível finalizar o cadastro. Tente novamente.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def custom_logout_view(request):
    auth_logout(request)
    messages.info(request, "Logout realizado com sucesso!")
    return redirect('home')
