"""LFG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('login', auth_views.LoginView.as_view(template_name='LFGCore/login.html')),
    path('logout', views.logout, name = 'logout'),
    path('accounts/profile/<int:id>', views.profile, name='profile_view'),
    path('accounts/profile/update', views.update_profile, name='profile_update'),
    path('accounts/create', views.signup, name='create_account'),
    path('search', views.search),
    path('project/<int:id>', views.project, name= 'project_view'), 
    path('project/create', views.project_create, name = 'project_create'),
    path('role/create', views.role_create, name='role_create'),
    path('role/delete', views.role_delete, name='role_delete'),
    path('role/apply/<int:id>', views.role_apply, name='role_apply'),
    path('', views.index, name='home'),
]
