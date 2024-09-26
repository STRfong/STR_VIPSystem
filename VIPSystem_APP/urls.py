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
from django.urls import path, include
from . import views 
from .views import VIPListView, VIPDetailView, VIPCreateView, VIPUpdateView, VIPDeleteView
from .views import ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView, ProjectParticipantsView
from .views import InviteListView, SendEmailListView, ProjectParticipantsEventTimeView, InviteListViewEventTime, SendEmailListViewEventTime
from .views import EventTimeDetailView
app_name = 'VIPSystem_APP'

urlpatterns = [
    path('respond/<str:token>/', views.handle_invitation_response, name='respond'),
    path('VIP_list/', include([
        path('', VIPListView.as_view(), name="vip_list"),
        path('create/', VIPCreateView.as_view(), name="vip_create"),
        path('create_from_excel/', views.vip_create_from_excel, name="vip_create_from_excel"),
        path('<int:vip_id>/', include([
            path('', VIPDetailView.as_view(), name="vip_detail"),
            path('update', VIPUpdateView.as_view(), name="vip_update"),
            path('delete', VIPDeleteView.as_view(), name="vip_delete"),
        ])),
    ])),
    path('project_list/', include([
        path('', ProjectListView.as_view(), name="project_list"), # project_list/
        path('create/', ProjectCreateView.as_view(), name="project_create"), # project_list/create/
        path('<int:project_id>/', include([
            path('', ProjectDetailView.as_view(), name="project_detail"), # project_list/<int:project_id>/
            path('update/', ProjectUpdateView.as_view(), name="project_update"), # project_list/<int:project_id>/update/
            path('delete/', ProjectDeleteView.as_view(), name="project_delete"), # project_list/<int:project_id>/delete/
            path('participants/', include([
                     path('', ProjectParticipantsView.as_view(), name="project_participants"), # project_list/<int:project_id>/participants/
                     path('<int:participant_id>/', include([   #####檢查到這裡#####
                        path('remove_participant/', views.remove_participant, name='remove_participant'), # project_list/<int:project_id>/participants/<int:participant_id>/remove_participant/
                        path('send_email/', views.send_email, name="send_email"), # project_list/<int:project_id>/participants/<int:participant_id>/send_email/
                     ])),
                 ])),
            path('invite_list/', InviteListView.as_view(), name="invite_list"), # project_list/<int:project_id>/invite_list/
            path('send_emails/', views.send_emails, name="send_emails"), # project_list/<int:project_id>/send_emails/
            path('send_emails_list/', SendEmailListView.as_view(), name="send_emails_list"), # project_list/<int:project_id>/send_emails_list/
            path('update_participants/', views.update_participants, name="update_participants"), # project_list/<int:project_id>/update_participants/
            path('event_time/<int:event_time_id>/', include([
                path('', EventTimeDetailView.as_view(), name="event_time_detail"),
                path('invite_list/', InviteListViewEventTime.as_view(), name="invite_list_event_time"),
                path('send_emails_list/', SendEmailListViewEventTime.as_view(), name="send_emails_list_event_time"),
                path('update_participants/', views.update_participants_event_time, name="update_participants_event_time"),
                path('send_emails/', views.send_emails_event_time, name="send_emails_event_time"),
                path('participants/', include([
                    path('', ProjectParticipantsEventTimeView.as_view(), name="project_participants_event_time"),
                    path('<int:participant_id>/', include([
                        path('remove_participant/', views.remove_participant_event_time, name='remove_participant_event_time'),
                        path('send_email/', views.send_email_event_time, name="send_email_event_time"),
                    ])),
                ])),
            ])),
        ])),
    ])),
]
