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
        card_number = self.cleaned_data.get('card_number')
        if card_number:
            card_number = card_number.replace(' ','').replace('-','')
        return card_number
    
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date:
            expiry_date = expiry_date.replace('/','').replace(' ','')

            if len(expiry_date) != 6:
                raise forms.ValidationError("Formato inválido. Use MM/AAAA")
            
            try:
                month = int(expiry_date[:2])
                year = int(expiry_date[2:])

                if month < 1 or month > 12:
                    raise forms.ValidationError("Mês inválido.")
                
                import datetime
                current_year = datetime.datetime.now().year
                current_month = datetime.datetime.now().month
                
                if year < current_year or (year == current_year and month < current_month):
                    raise forms.ValidationError("Cartão expirado")
            
            except ValueError:
                raise forms.ValidationError("Data inválida")
        
        return expiry_date
    
class CustomerInfoForm(forms.Form):
    full_name = forms.CharField(
        label="Nome Completo",
        max_length=100
    )
    email = forms.EmailField(
        label="E-mail",
        max_length=100
    )
    cpf = forms.CharField(
        label="CPF",
        max_length=14,
        widget=forms.TextInput(attrs={'placeholder': '123.456.789-00'})
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            cpf = cpf.replace('.','').replace('-','')
            if len(cpf) != 11:
                raise forms.ValidationError("CPF incompleto")
            
        if len(set(cpf)) == 1:
            raise forms.ValidationError("CPF inválido")
    
        return cpf
    
    