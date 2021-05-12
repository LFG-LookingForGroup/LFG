from django.utils import translation
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from pathlib import Path
from LFGCore.models import *
from LFGCore.forms import SignUpForm, UpdateUserForm, UpdateProfileForm, ProjectForm, ProjectRoleForm, UpdateProjectForm
from datetime import datetime

def about(request):
      return render(request, "LFGCore/about.html", {'logged_in' : request.user.is_authenticated})

@login_required
def account(request):
  return render(request, "LFGCore/account.html", {'logged_in' : request.user.is_authenticated})

@login_required
def profile(request, id=None):
  user = None
  if id == None:
    user = request.user
  else:
    user = User.objects.get(id=id)
  
  return render(request, 'LFGCore/profile.html', {
    "user": user,
    "is_own_profile": user == request.user,
    "memberships" : user.profile.member_set.filter(active=True, project__active=True),
    "skillset": user.profile.get_resume(), 
    'logged_in' : request.user.is_authenticated 
  })

@login_required
def project(request, id=None):
  if id == None:
    return HttpResponseNotFound()
  else:
    project = Project.objects.get(id=id)
    if project == None or not project.active:
      return HttpResponseNotFound(f"<p>Project id {id} does not exist</p>")

  role_form = ProjectRoleForm(initial={'project' : project})
  membership = request.user.profile.member_set.filter(project=project)
  is_owner = False
  if not membership.exists():
    membership = None
  else:
    membership = membership.first()
    is_owner = membership.is_owner
  role_list = project.applicable_role_list(request.user)

  return render(request, 'LFGCore/project.html', {
    "user" : request.user, 
    "membership" : membership, 
    "is_owner" : is_owner,
    "project" : project, 
    "members" : project.member_set.filter(active=True),
    "role_list" : role_list,
    "role_form" : role_form,
    'logged_in' : request.user.is_authenticated
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
    to_delete.deactivate()
    return redirect(f'/project/{project_id}/')

@login_required
def role_apply(request, id):
  if request.method != 'POST':
    return HttpResponseNotFound()
  elif not Role.objects.filter(id=id).exists():
    return HttpResponseNotFound()
  else:
    role = Role.objects.get(id=id)
    application = role.apply(request.user)
    if application is None:
      return HttpResponseNotFound()
    else:
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
    application.graduate_to_membership()
    return redirect('/accounts/profile/')

@login_required
def quit_membership(request, member_id):
  if not Member.objects.filter(id=member_id).exists():
    return HttpResponseNotFound()
  
  delete_membership = Member.objects.get(id=member_id)
  request_membership = Member.objects.filter(profile=request.user.profile, project=delete_membership.project)

  if not request_membership.exists():
    return HttpResponseNotFound()

  request_membership = request_membership.first()

  if request_membership.is_owner:
    if request_membership == delete_membership:
      delete_membership.project.deactivate()
      return redirect('/')
    else:
      delete_membership.deactivate()
      return redirect(f'/project/{request_membership.project.id}/')
  
  if request_membership == delete_membership:
    delete_membership.deactivate()

    return redirect('/accounts/profile/')

  return HttpResponseNotFound()

@login_required
def project_create(request):
  if request.method == 'POST':
    form = ProjectForm(request.POST)
    if form.is_valid():
      new_project = form.save()
      new_project.set_creator(request.user)
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
  project = Project.objects.get(id=id)
  if request.method == 'POST':
    project_form = UpdateProjectForm(request.POST, instance=project)
    if project_form.is_valid():
      project_form.save()
      messages.success(request, 'Project was updated successfully.')
      return redirect(f'/project/{id}/')
    else:
      messages.error(request, 'Project was not updated.')
  else:
    project_form = UpdateProjectForm(instance=project)
  return render(request, 'LFGCore/projectUpdate.html', {
    'project_form' : project_form,
    'logged_in' : request.user.is_authenticated
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
    if request.POST['update-type'] == 'profile':
      user_form = UpdateUserForm(request.POST, instance=request.user)
      profile_form = UpdateProfileForm(request.POST, instance=request.user.profile)
      password_form = PasswordChangeForm(request.user)
      if user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, 'Profile was updated successfully.')
        return redirect('/accounts/profile/')
      else:
        messages.error(request, 'Profile was not updated.')
    elif request.POST['update-type'] == 'password':
      password_form = PasswordChangeForm(request.user, request.POST)
      if password_form.is_valid():
        user = password_form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed successfully.')
        return redirect('/accounts/profile/')
      else:
        messages.error(request, 'Password could not be updated.')
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
  else:
    user_form = UpdateUserForm(instance=request.user)
    profile_form = UpdateProfileForm(instance=request.user.profile)
    password_form = PasswordChangeForm(request.user)
  return render(request, 'LFGCore/profileUpdate.html', {
    'user_form' : user_form,
    'profile_form' : profile_form,
    'password_form': password_form,
    'logged_in' : request.user.is_authenticated
  })

def search(request):
  if request.method != 'GET':
    return HttpResponseNotFound("<h1>Only GETS allowed</h1>")

  query = request.GET.get('query', None)

  if query != None and query.strip() != "":
    search_result_project = Project.objects.filter(Q(name__icontains=query) & Q(active=True))
    search_result_user = User.objects.filter((Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)))

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
def advanced_search(request):    

  project_search_performed = False
  project_results = Project.objects.all()
  if 'project_contains' in request.GET and request.GET['project_contains'] != "":
    project_results = project_results.filter(name__icontains = request.GET['project_contains'])
    project_search_performed = True
  if 'project_exact' in request.GET and request.GET['project_exact'] != "":
    project_results = project_results.filter(name__iexact=request.GET['project_exact'])
    project_search_performed = True
  if 'skill' in request.GET and request.GET['skill'] != "None":
    try:
      skill = Skill.objects.get(id=int(request.GET['skill']))
      # project_results = project_results.filter(role_set__skills=skill)
      project_results = filter(lambda p: skill in p.skill_set(), project_results) # Wish this could be done with a Django query
      project_search_performed = True
    except ValueError:
      pass

  if not project_search_performed:
    project_results = []

  user_search_performed = False
  user_results = User.objects.all()
  if 'user_name' in request.GET and request.GET['user_name'] != "":
    user_results = user_results.filter(username__icontains=request.GET['user_name'])
    user_search_performed = True
  if 'first_name' in request.GET and request.GET['first_name'] != "":
    user_results = user_results.filter(first_name__icontains=request.GET['first_name'])
    user_search_performed = True
  if 'last_name' in request.GET and request.GET['last_name'] != "":
    user_results = user_results.filter(last_name__icontains=request.GET['last_name'])
    user_search_performed = True

  if not user_search_performed:
    user_results = []

  return render(request, "LFGCore/advanced.html", {
    'logged_in' : request.user.is_authenticated,
    'skills' : Skill.objects.all(),
    'project_results' : project_results,
    'user_results' : user_results
  })

# @login_required
# @transaction.atomic
# def apply(request):
  
#   return render(request, 'LFGCore/project.html', {
#     "project" : project,
#     'logged_in' : request.user.is_authenticated
#   })

