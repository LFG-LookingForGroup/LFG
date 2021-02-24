from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from LFGCore.models import *

class SignUpForm(UserCreationForm):
    birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    first_name = forms.CharField(max_length=30, required= True, help_text='Please provide your legal first name.')
    last_name = forms.CharField(max_length=30, required = True, help_text='Please provide your legal surname.')
    email = forms.EmailField(max_length =254, help_text = 'Please provide a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name','email', 'birth_date', 'password1', 'password2', )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio',)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'start_date', 'end_date', )

class ProjectRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('title', 'description', 'project', 'skills')

    def __init__(self, *args, **kwargs):
        super(ProjectRoleForm, self).__init__(*args, **kwargs)
        self.fields['project'].widget = forms.HiddenInput()
        self.fields['skills'] = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.SelectMultiple())