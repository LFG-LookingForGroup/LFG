from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    first_name = forms.CharField(max_length=30, required= True, help_text='Please provide your legal first name.')
    last_name = forms.CharField(max_length=30, required = True, help_text='Please provide your legal surname.')
    email = forms.EmailField(max_length =254, help_text = 'Please provide a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name','email', 'birth_date', 'password1', 'password2', )