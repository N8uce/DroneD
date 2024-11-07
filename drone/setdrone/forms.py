from .models import Order
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity', 'city', 'street', 'house']
        widgets = {
            'city': forms.TextInput(attrs={'placeholder': 'Введите город...'}),
            'street': forms.TextInput(attrs={'placeholder': 'Введите улицу...'}),
            'house': forms.TextInput(attrs={'placeholder': 'Введите дом...'}),
        }



class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    pass











