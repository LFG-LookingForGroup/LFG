from django.utils import translation
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from LFGCore.models import *
from LFGCore.forms import SignUpForm
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
