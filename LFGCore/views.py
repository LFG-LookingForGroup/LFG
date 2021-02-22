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
from LFGCore.forms import SignUpForm, UserForm, ProfileForm, ProjectForm
import datetime


@login_required
def account(request):
  return render(request, "LFGCore/account.html")

@login_required
def profile(request):
  skills = []
  for member in request.user.profile.member_set:
    for role in member.roles:
      for skill in role.skills:
        if skill.name not in skills:
          skills.append(skill.name)
  return render(request, 'LFGCore/profile.html', {"user":request.user, "user_skills":skills})

@login_required
def project(request, id=None):
  if id == None:
    return HttpResponseNotFound()
  else:
    project = Project.objects.get(id=id)
    if project == None:
      return HttpResponseNotFound(f"<p>Project id {id} does not exist</p>")

  return render(request, 'LFGCore/project.html', {"project" : project })

@login_required
def project_create(request):
  if request.method == 'POST':
    form = ProjectForm(request.POST)
    if form.is_valid():
      new_project = form.save()
      request.user.profile.projects.add(new_project, through_defaults={"is_owner": True, "startDate": datetime.date.today()})
      return redirect(f'project/{new_project.id}')
  else:
    form = ProjectForm()
  return render(request, 'LFGCore/createProject.html', {'form' : form})

@login_required
@transaction.atomic
def update_project(request, project_id, user_id):
  if request.method == 'POST':
    project_form = ProjectForm(request.POST, instance=request.user)
    if project_form.is_valid():
      project_form.save()
      messages.success(request, 'Project was updated successfully.')
      return redirect('project_view')
    else:
      messages.error(request, 'Project was not updated.')
  else:
    project_form = ProjectForm(instance=request.user)
  return render(request, 'LFGCore/projectUpdate.html', {
    'project_form' : project_form,
  })

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
def logout(request):
  logout(request)
  redirect('')

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
      return redirect('profile_view')
    else:
      messages.error(request, 'Profile was not updated.')
  else:
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request)
  return render(request, 'LFGCore/profileUpdate.html', {
    'user_form' : user_form,
    'profile_form' : profile_form
  })

def search(request):
  if request.method != 'GET':
    return HttpResponseNotFound("<h1>Only GETS allowed</h1>")

  query = request.GET.get('query', None)

  if query != None and query.strip() != "":
    search_result = Project.objects.filter(name__icontains=query)

    return render(request, 'LFGCore/search.html', {'search_results' : search_result, 'original_query' : query})
  return render(request, 'LFGCore/search.html')

def index(request):
  return render(request, "LFGCore/index.html")
