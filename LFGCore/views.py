from django.utils import translation
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from pathlib import Path
from LFGCore.models import *
from LFGCore.forms import SignUpForm, UserForm, ProfileForm, ProjectForm, ProjectRoleForm
import datetime


@login_required
def account(request):
  return render(request, "LFGCore/account.html")

@login_required
def profile(request, id=None):
  user = None
  if id == None:
    user = request.user
  else:
    user = User.objects.get(id=id)
  
  return render(request, 'LFGCore/profile.html', {"user": user, "user_skills":[], 'logged_in' : request.user.is_authenticated })

@login_required
def project(request, id=None):
  if id == None:
    return HttpResponseNotFound()
  else:
    project = Project.objects.get(id=id)
    if project == None:
      return HttpResponseNotFound(f"<p>Project id {id} does not exist</p>")

  role_form = ProjectRoleForm(initial={'project' : project})
  return render(request, 'LFGCore/project.html', {"project" : project , "role_form" : role_form })

@login_required
def role_create(request):
  if request.method == 'POST':
    role_form = ProjectRoleForm(request.POST)
    if role_form.is_valid():
      new_role = role_form.save()
      return redirect(f'/project/{new_role.project.id}')
  else:
    return HttpResponseNotFound()

@login_required
def role_delete(request):
  if request.method != 'POST':
    return HttpResponseNotFound()
  elif not Role.objects.filter(id=request.POST['id']).exists():
    return HttpResponseNotFound()
  else:
    to_delete = Role.objects.get(id=request.POST['id'])
    project_id = to_delete.project.id
    to_delete.delete()
    return redirect(f'/project/{project_id}')

@login_required
def role_apply(request, id=None):
  if id == None:
    return HttpResponseNotFound()
  elif request.method != 'POST':
    return HttpResponseNotFound()
  elif not Role.objects.filter(id=id).exists():
    return HttpResponseNotFound()
  elif request.user.profile.applications.filter(id=id).exists():
    return HttpResponseNotFound()
  else:
    role = Role.objects.get(id=id)
    request.user.profile.applications.add(role, through_defaults={ "status": 'A' })
    return redirect(f'/search/?query={request.POST["query"]}')

@login_required
def application_update_status(request, id):
  if request.method != 'POST':
    return HttpResponseNotFound()
  elif not Application.objects.filter(id=id).exists():
    return HttpResponseNotFound()
  elif request.POST.get('newstatus', '') not in map(lambda t: t[0], Application._meta.get_field('status').choices):
    return HttpResponseNotFound()
  else:
    application = Application.objects.get(id=id)
    application.status = request.POST['newstatus']
    application.save()
    return redirect(f'/project/{application.role.project.id}/' )

@login_required
def project_create(request):
  if request.method == 'POST':
    form = ProjectForm(request.POST)
    if form.is_valid():
      new_project = form.save()
      request.user.profile.projects.add(new_project, through_defaults={"is_owner": True, "start_date": datetime.date.today()})
      return redirect(f'/project/{new_project.id}')
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
      return redirect('')
  else:
    form = SignUpForm()
  return render(request, 'LFGCore/signup.html', {'form' : form, 'logged_in' : request.user.is_authenticated })

@login_required
def logout_user(request):
  logout(request)
  return redirect('/')

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
    search_result_project = Project.objects.filter(name__icontains=query)
    search_result_user = User.objects.filter(username__icontains=query)

    return render(request, 'LFGCore/search.html', {'search_results_project' : search_result_project, 'search_results_user' : search_result_user , 'original_query' : query, 'user' : request.user, 'logged_in' : request.user.is_authenticated })
  return render(request, 'LFGCore/search.html', { 'logged_in' : request.user.is_authenticated })

def index(request):
  return render(request, "LFGCore/index.html", { 'logged_in' : request.user.is_authenticated })

@login_required
@transaction.atomic
def apply(request):
  
  return render(request, 'LFGCore/project.html', {"project" : project })

