from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from LFGCore.models import *

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required= True, help_text='Please provide your legal first name.')
    last_name = forms.CharField(max_length=30, required = True, help_text='Please provide your legal surname.')
    email = forms.EmailField(max_length =254, help_text = 'Please provide a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class UpdateUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', )

class UpdateProfileForm(forms.ModelForm):
    bio = forms.CharField(max_length=1000, required=False)
    telephone_number = forms.DecimalField(max_digits=11, decimal_places=0, required=False)

    class Meta:
        model = Profile
        fields = ('bio', 'telephone_number', )

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', )

class UpdateProjectForm(forms.ModelForm):
    name = forms.CharField(max_length = 100, required=True)
    description = forms.CharField(max_length = 1000, required=False)

    class Meta:
        model = Project
        fields = ('name', 'description', )

class ProjectRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('title', 'description', 'project', 'skills')

    def __init__(self, *args, **kwargs):
        super(ProjectRoleForm, self).__init__(*args, **kwargs)
        self.fields['project'].widget = forms.HiddenInput()
        self.fields['skills'] = forms.ModelMultipleChoiceField(queryset=Skill.objects.all(), widget=forms.SelectMultiple())