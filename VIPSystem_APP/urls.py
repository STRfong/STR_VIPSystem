"""
URL configuration for VIPSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from . import views 
from .views import VIPListView, VIPDetailView, VIPCreateView, VIPUpdateView, VIPDeleteView
from .views import ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView, ProjectParticipantsView
from .views import InviteListView, SendEmailListView
app_name = 'VIPSystem_APP'

urlpatterns = [
    path('respond/<str:token>/', views.handle_invitation_response, name='respond'),
    path('VIP_list', VIPListView.as_view(), name="vip_list"),
    path('VIP_list/create/', VIPCreateView.as_view(), name="vip_create"), # 新增
    path('VIP_list/create_from_excel/', views.vip_create_from_excel, name="vip_create_from_excel"), # 新增
    path('VIP_list/<int:pk>/', VIPDetailView.as_view(), name="vip_id"),
    path('VIP_list/<int:pk>/update/', VIPUpdateView.as_view(), name="vip_update"),
    path('VIP_list/<int:vip_id>/delete/', VIPDeleteView.as_view(), name="vip_delete"),
    path('project_list', ProjectListView.as_view(), name="project_list"),
    path('project_list/create/', ProjectCreateView.as_view(), name="project_create"), # 新增
    path('project_list/<int:pk>/', ProjectDetailView.as_view(), name="project_id"),
    path('project_list/<int:pk>/participants/', ProjectParticipantsView.as_view(), name="project_participants"),
    path('project_list/<int:project_id>/participants/send_email/', views.send_email, name="send_email"),
    path('project_list/<int:project_id>/invite_list/', InviteListView.as_view(), name="invite_list"),
    path('project_list/<int:project_id>/send_emails_list/', SendEmailListView.as_view(), name="send_emails_list"),
    path('project_list/<int:project_id>/update_participants/', views.update_participants, name="update_participants"),
    path('project_list/<int:project_id>/send_emails/', views.send_emails, name="send_emails"),
    path('project_list/<int:pk>/update/', ProjectUpdateView.as_view(), name="project_update"),
    path('project_list/<int:pk>/delete/', ProjectDeleteView.as_view(), name="project_delete"),
    path('project_list/<int:project_id>/remove_participant/<int:participant_id>/', views.remove_participant, name='remove_participant'),
]
