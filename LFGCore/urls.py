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
    path('login/', auth_views.LoginView.as_view(template_name='LFGCore/login.html')),
    path('logout/', views.logout_user, name = 'logout'),
    path('about/', views.about, name = 'about'),
    path('accounts/profile/', views.profile, name='my_profile_view'),
    path('accounts/profile/<int:id>/', views.profile, name='profile_view'),
    path('accounts/profile/update/', views.update_profile, name='profile_update'),
    path('accounts/create/', views.signup, name='create_account'),
    path('search/', views.search),
    path('project/<int:id>/', views.project, name= 'project_view'),
    path('project/create/', views.project_create, name = 'project_create'),
    path('project/update/<int:id>/', views.update_project, name = 'project_update'),
    path('project/acceptoffer/<int:application_id>/', views.accept_offer, name = 'accept_offer'),
    path('role/create/', views.role_create, name='role_create'),
    path('role/delete/', views.role_delete, name='role_delete'),
    path('role/apply/<int:id>/', views.role_apply, name='role_apply'),
    path('membership/quit/<int:member_id>/', views.quit_membership, name='member_quit'),
    path('application/updatestatus/<int:id>/', views.application_update_status, name='application_update_status'),
    path('advanced/', views.advanced_search, name='advanced_search'), 
    path('', views.index, name='home')
]
