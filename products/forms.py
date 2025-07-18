from django import forms
from datetime import datetime
from .models import Purchases
import re



class PaymentMethodForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=Purchases.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Método de Pagamento",
        error_messages={'required': 'Método de pagamento é obrigatório.'}
    )

    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 5678 9012 3456'})
    )

    card_expiration = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/AA'})
    )

    card_cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123'})
    )

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        payment_method = self.cleaned_data.get('payment_method')

        if payment_method == 'credit_card':
            if not card_number:
                raise forms.ValidationError("Número do cartão é obrigatório para pagamento com cartão de crédito.")

            card_number = re.sub(r'\D', '', card_number)

            if len(card_number) < 13 or len(card_number) > 19:
                raise forms.ValidationError("Número do cartão deve ter entre 13 e 19 dígitos.")

            if not self.luhn_validate(card_number):
                raise forms.ValidationError("Número do cartão inválido.")

        return card_number

    def clean_card_expiration(self):
        card_expiration = self.cleaned_data.get('card_expiration')
        payment_method = self.cleaned_data.get('payment_method')
        
        if payment_method == 'credit_card':
            if not card_expiration:
                raise forms.ValidationError('Data de expiração é obrigatória para cartão de crédito.')
            
            if not re.match(r'^\d{2}/\d{2}$', card_expiration):
                raise forms.ValidationError('Data deve estar no formato MM/AA')
    
            month, year = card_expiration.split('/')
            month, year = int(month), int('20' + year)  # ✅ Corrigido: duas variáveis separadas
            
            if month < 1 or month > 12:
                raise forms.ValidationError('Mês inválido')
    
            current_date = datetime.now()
            if year < current_date.year or (year == current_date.year and month < current_date.month):
                raise forms.ValidationError('Cartão expirado')
        
        return card_expiration

    def clean_card_cvv(self):
        card_cvv = self.cleaned_data.get('card_cvv')
        payment_method = self.cleaned_data.get('payment_method')
    
        if payment_method == 'credit_card':
            if not card_cvv:
                raise forms.ValidationError("CVV é obrigatório para cartão de crédito.")
            
            if not re.match(r'^\d{3,4}$', card_cvv):
                raise forms.ValidationError("CVV deve ter 3 ou 4 dígitos.")
        return card_cvv
    
    def luhn_validate(self, card_number):
        # Luhn algorithm para validar o número do cartão de crédito
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0


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
    
    