from django.utils import translation
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from pathlib import Path
from LFGCore.models import *
from LFGCore.forms import SignUpForm, UserForm, ProfileForm
import datetime


@login_required
def account(request):
  return render(request, "LFGCore/account.html")

@login_required
def profile(request):
    return render(request, 'LFGCore/profile.html', {"user":request.user})

@login_required
def project(request, projectid):
  pass

def signup(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data.get('username')
      raw_password = form.cleaned_data.get('password1')
      user = authenticate(username = username, password = raw_password)
      login(request, user)
      return redirect('home')
  else:
    form = SignUpForm()
  return render(request, 'LFGCore/signup.html', {'form' : form})

@login_required
@transaction.atomic
def update_profile(request, user_id):
  if request.method == 'POST':
    user_form = UserForm(request.POST, instance=request.user)
    profile_form = ProfileForm(request.POST, instance=request.user.profile)
    if user_form.is_valid() and profile_form.is_valid():
      user_form.save()
      profile_form.save()
      messages.success(request, 'Profile was updated successfully.')
      return redirect('settings:profile')
    else:
      messages.error(request, 'Profile was not updated.')
  else:
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request)
  return render(request, 'profile/profile1.html', {
    'user_form' : user_form,
    'profile_form' : profile_form
  })

def search(request):
  if request.method != 'GET':
    return HttpResponseNotFound("<h1>Only GETS allowed</h1>")

  query = request.GET.get('query', None)

  if query != None and query.strip() != "":
    search_result = Project.objects.filter(name__icontains=query)

    rows = [f"""
      <tr>
        <th>{p.name}</th>
        <th>{p.description}</th>
      </tr>""" for p in search_result]

    rendered_results = f"""
      <table>
        <tr>
          <td>Name</td>
          <td>Description</td>
        </tr>
        {"".join(rows)}
      </table>"""

    return render(request, 'LFGCore/search.html', {'search_results' : rendered_results, 'original_query' : query})
  return render(request, 'LFGCore/search.html')

def index(request):
  return render(request, "LFGCore/top.html")
