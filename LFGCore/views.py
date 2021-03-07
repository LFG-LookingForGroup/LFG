from django.utils import translation
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from pathlib import Path
from LFGCore.models import *
from LFGCore.forms import SignUpForm, UpdateUserForm, UpdateProfileForm, ProjectForm, ProjectRoleForm
from datetime import datetime


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
  
  return render(request, 'LFGCore/profile.html', {
    "user": user, 
    "skillset": user.profile.get_resume(), 
    'logged_in' : request.user.is_authenticated 
  })

@login_required
def project(request, id=None):
  if id == None:
    return HttpResponseNotFound()
  else:
    project = Project.objects.get(id=id)
    if project == None:
      return HttpResponseNotFound(f"<p>Project id {id} does not exist</p>")

  role_form = ProjectRoleForm(initial={'project' : project})
  membership = request.user.profile.member_set.filter(project=project)
  is_owner = False
  if not membership.exists():
    membership = None
  else:
    membership = membership[0]
    is_owner = membership.is_owner
  role_list = project.applicable_role_list(request.user)

  return render(request, 'LFGCore/project.html', {
    "user" : request.user, 
    "membership" : membership, 
    "is_owner" : is_owner,
    "project" : project, 
    "role_list" : role_list,
    "role_form" : role_form 
  })

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
def role_apply(request, id):
  if request.method != 'POST':
    return HttpResponseNotFound()
  elif not Role.objects.filter(id=id).exists():
    return HttpResponseNotFound()
  else:
    role = Role.objects.get(id=id)
    if request.user.profile.applications.filter(id=id).exists():
      application = request.user.profile.application_set.get(role=role)
      if application.status == 'R':
        application.status = 'A'
        application.save()
        return redirect(request.POST['redirect'])
      else:
        return HttpResponseNotFound()
    else:
      role = Role.objects.get(id=id)
      request.user.profile.applications.add(role, through_defaults={ "status": 'A' })
      return redirect(request.POST['redirect'])

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
def accept_offer(request, application_id):
  if request.method != 'POST':
    return HttpResponseNotFound()
  elif not Application.objects.filter(id=application_id).exists():
    return HttpResponseNotFound()
  else:
    application = Application.objects.get(id=application_id)
    application.applicant.projects.add(application.role.project, through_defaults={ "is_owner": False, "start_date": datetime.now(timezone.utc) })
    membership = Member.objects.get(project=application.role.project, profile=application.applicant)
    membership.roles.add(application.role)
    application.delete()
    return redirect('/accounts/profile/')

@login_required
def quit_membership(request, member_id):
  if not Member.objects.filter(id=member_id).exists():
    return HttpResponseNotFound()
  
  delete_membership = Member.objects.get(id=member_id)
  request_membership = Member.objects.filter(profile=request.user.profile, project=delete_membership.project)

  if not request_membership.exists():
    return HttpResponseNotFound()

  request_membership = request_membership[0]

  if request_membership.is_owner:
    if request_membership == delete_membership:
      delete_membership.project.delete()
      return redirect('/')
    else:
      delete_membership.delete()
      return redirect(f'/project/{request_membership.project.id}/')
  
  if request_membership == delete_membership:
    delete_membership.delete()

    return redirect('/accounts/profile/')

  return HttpResponseNotFound()

@login_required
def project_create(request):
  if request.method == 'POST':
    form = ProjectForm(request.POST)
    if form.is_valid():
      new_project = form.save()
      new_role = Role.objects.create(project=new_project, title="Creator", description="Creator of the project.")
      request.user.profile.projects.add(new_project, through_defaults={"is_owner": True, "start_date": datetime.now(timezone.utc)})
      membership = request.user.profile.member_set.get(project=new_project)
      membership.roles.add(new_role)
      return redirect(f'/project/{new_project.id}')
  else:
    form = ProjectForm()
  return render(request, 'LFGCore/createProject.html', {
    'form' : form, 
    'logged_in' : request.user.is_authenticated 
  })

@login_required
@transaction.atomic
def update_project(request, id):
  if request.method == 'POST':
    project = Project.objects.get(id=id)
    project_form = ProjectForm(request.POST, instance=project)
    if project_form.is_valid():
      project_form.save()
      messages.success(request, 'Project was updated successfully.')
      return redirect(f'/project/{id}/')
    else:
      messages.error(request, 'Project was not updated.')
  else:
    project_form = ProjectForm(instance=request.user)
  return render(request, 'LFGCore/projectUpdate.html', {
    'project_form' : project_form,
  })

def signup(request):
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      form.save()
      username = form.cleaned_data.get('username')
      raw_password = form.cleaned_data.get('password1')
      user = authenticate(username = username, password = raw_password)
      login(request, user)
      return redirect('/')
  else:
    form = SignUpForm()
  return render(request, 'LFGCore/signup.html', {
    'form' : form, 
    'logged_in' : request.user.is_authenticated 
  })

@login_required
def logout_user(request):
  logout(request)
  return redirect('/')

@login_required
@transaction.atomic
def update_profile(request):
  if request.method == 'POST':
    user_form = UpdateUserForm(request.POST, instance=request.user)
    profile_form = UpdateProfileForm(request.POST, instance=request.user.profile)
    if user_form.is_valid() and profile_form.is_valid():
      profile_form.save()
      if user_form.cleaned_data.get("password1") != "":
        user_form.save()
        user = authenticate(username = user_form.cleaned_data.get('username'), password = user_form.cleaned_data.get('password'))
        login(request, user)
      else:
        request.user.username = user_form.cleaned_data.get('username')
        request.user.first_name = user_form.cleaned_data.get('first_name')
        request.user.last_name = user_form.cleaned_data.get('last_name')
        request.user.email = user_form.cleaned_data.get('email')
        request.user.save()
      messages.success(request, 'Profile was updated successfully.')
      return redirect('/accounts/profile/')
    else:
      messages.error(request, 'Profile was not updated.')
  else:
    user_form = UpdateUserForm(instance=request.user)
    profile_form = UpdateProfileForm(instance=request.user.profile)
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
    search_result_user = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))

    search_result_project = [(proj, proj.applicable_role_list(request.user)) for proj in search_result_project]

    return render(request, 'LFGCore/search.html', {
      'search_results_project' : search_result_project, 
      'search_results_user' : search_result_user, 
      'original_query' : query, 'user' : request.user, 
      'logged_in' : request.user.is_authenticated 
    })
  return render(request, 'LFGCore/search.html', { 
    'logged_in' : request.user.is_authenticated 
  })

def index(request):
  return render(request, "LFGCore/index.html", { 
    'logged_in' : request.user.is_authenticated 
  })

@login_required
@transaction.atomic
def apply(request):
  
  return render(request, 'LFGCore/project.html', {
    "project" : project 
  })

