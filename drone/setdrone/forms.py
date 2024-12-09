from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import Order, OrderItem, Profile
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['city', 'street', 'house']
        widgets = {
            'city': forms.TextInput(attrs={'placeholder': 'Введите город...'}),
            'street': forms.TextInput(attrs={'placeholder': 'Введите улицу...'}),
            'house': forms.TextInput(attrs={'placeholder': 'Введите дом...'}),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']



class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Use get_or_create to avoid duplicate profile creation
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data['phone_number']
            profile.save()

        return user

class LoginForm(AuthenticationForm):
    pass











