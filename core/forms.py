from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nome de Utilizador ou Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome de utilizador ou email'
        })
    )
    password = forms.CharField(
        label="Palavra-passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua palavra-passe'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="Endereço de email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'exemplo@dominio.com'
        })
    )

    first_name = forms.CharField(
        label="Primeiro Nome",
        max_length=30,
        required=False, # Defina como True se quiser obrigatório
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu primeiro nome'})
    )

    last_name = forms.CharField(
         label="Último Nome",
         max_length=150,
         required=True,  
         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu último nome'})
     )

class Meta(UserCreationForm.Meta):
    model = User
    fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = "Username"
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Crie um nome de utilizador único',
            'class': 'form-control' # Garante a classe do Bootstrap
        })
        self.fields['password1'].label = "Crie uma Palavra-passe"
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Mínimo de 8 caracteres',
            'class': 'form-control'
        })
        self.fields['password2'].label = "Confirme a Palavra-passe"
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Digite a palavra-passe novamente',
            'class': 'form-control'
        }) 

        if 'email' in self.fields:
            self.fields['email'].widget.attrs.update({ 'class': 'form-control' })