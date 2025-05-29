from django import forms
from .models import Purchases

class PaymentMethodForm(forms.Form):

    payment_method = forms.CharField(
        choices=Purchases.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        label="Método de Pagamento"
    )

class CreditCardForm(forms.Form):

    card_number = forms.CharField(
        label="Número do Cartão",
        max_length=19,
        widget=forms.TextInput(attrs={'placeholder': 'XXXX XXXX XXXX XXXX'})
    )

    card_holder = forms.CharField(
        label="Nome no Cartão",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'NOME COMO ESTÁ NO CARTÃO'})
    )

    expiry_date = forms.CharField(
        label="Data de Validade",
        max_length=7,
        widget=forms.TextInput(attrs={'placeholder': 'MM/AAAA'})
    )

    cvv = forms.CharField(
        label="Código de Segurança (CVV)",
        max_length=4,
        widget=forms.TextInput(attrs={'placeholder': '123'})
    )

    installments = forms.ChoiceField(
        label="Parcelas",
        choices=[(i, f'{i}x') for i in range(1,13)],
        initial=1
    )

    def clean_card_number(self):
        pass