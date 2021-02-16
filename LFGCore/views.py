from django.utils import translation
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from LFGCore.models import *
import datetime

@csrf_exempt
def logout_user(request):
  return HttpResponse()

@login_required
def account(request):
  return render(request, "LFGCore/account.html")

@login_required
def profile(request):
    return render(request, 'LFGCore/profile.html', {"user":request.user})

def signup(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data.get('username')
      raw_password = form.cleaned_data.get('password')
      user = authenticate(username = username, password = raw_password)
      login(request, user)
      return redirect('home')
  else:
    form = UserCreationForm()
  return render(request, 'LFGCore/main.html', {'form' : form})

def search(request):
  return render(request, 'LFGCore/search.html')

def index(request):
  return render(request, "LFGCore/top.html")
