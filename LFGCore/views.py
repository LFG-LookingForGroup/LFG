from django.utils import translation
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from LFGCore.models import *
import datetime

@csrf_exempt
def login_user(request):

  print(translation.get_language_from_request(request))
  print("=" * 50)

  # Check if POST request
  if request.method != 'POST':
    return JsonResponse({
      'success' : False,
      'reason' : 'Login requests must be POSTs'
    })

  # Check to make sure user is not already logged in
  if request.user.is_authenticated():
    return JsonResponse({
      'success' : False,
      'reason' : 'User is already logged in'
    })

  # Check to see if username & password are provided
  if not all(prop in request.POST for prop in ['username', 'password']):
    return JsonResponse({
      'success' : False,
      'reason' : 'Please specify a username and a password to log in'
    })

  user = authenticate(username=request.POST['username'], password=request.POST['password'])
  
  # Check if username & password are valid
  if user is None:
    return JsonResponse({
      'success' : False,
      'reason' : 'Invalid username and/or password'
    })
  
  # Log user in
  login(request, user)

  return JsonResponse({
    'success' : True
  })

@csrf_exempt
def logout_user(request):
  return HttpResponse()

def account(request):
  return render(request, "Account/account.html")

def profile(request):
  return render(request, "Profile/profile.html")

def search(request):
  return render(request, 'Search/search.html')

def index(request):
  return render(request, "Top/top.html")
