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
from .views import VIPListView, VIPDetailView, VIPCreateView, VIPUpdateView, VIPDeleteView, UpdateVipInfoByEventTimeView
from .views import ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView, ProjectParticipantsView, ProjectParticipationBySectionView
from .views import InviteListView, SendEmailListBySectionView, ProjectParticipantsByEventTimeView, InviteListViewEventTime, SendEmailListViewEventTime, InviteListBySectionView, UpdateParticipantsBySectionView, UpdateParticipantsInfoBySectionView, UpdateParticipantsInfoByEventTimeView, UpdateParticipantsByEventTimeView
from .views import UpdateParticipantsByEventTimeView, UpdateParticipantsByEventTimeDirectlyView
from .views import EventTimeDetailView, EventTimeCreateView, UpdateEventTimeView, DeleteEventTimeView, send_email_by_section, ExportParticipantsByEventTimeView    
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
            path('create_event_time/', EventTimeCreateView.as_view(), name="create_event_time"), # project_list/<int:project_id>/create_event_time/
            path('update_event_time/', UpdateEventTimeView.as_view(), name='update_event_time'),
            path('delete_event_time/', DeleteEventTimeView.as_view(), name='delete_event_time'),
            path('invite_list/', InviteListView.as_view(), name="invite_list"), # project_list/<int:project_id>/invite_list/
            path('<str:section>/', include([
                path('participants/', ProjectParticipationBySectionView.as_view(), name='participation_by_section'),
                path('remove_participant/', views.remove_participant_by_section, name='remove_participant_by_section'), # project_list/<int:project_id>/participants/<int:participant_id>/remove_participant/
                path('invite_list/', InviteListBySectionView.as_view(), name='invite_list_by_section'),
                path('update_participants/', UpdateParticipantsBySectionView.as_view(), name='update_participants_by_section'),
                path('update_participants_info/', UpdateParticipantsInfoBySectionView.as_view(), name='update_participants_info_by_section'),
                path('send_email/', views.send_email_by_section, name='send_email_by_section'),
                path('send_emails_list/', SendEmailListBySectionView.as_view(), name="send_emails_list_by_section"), # project_list/<int:project_id>/send_emails_list/
                path('send_emails/', views.send_emails_by_section, name='send_emails_by_section'),
                path('event_time/<int:event_time_id>/', include([
                    path('participants/', ProjectParticipantsByEventTimeView.as_view(), name="participation_by_event_time"),
                    path('remove_participant/', views.remove_participant_event_time, name='remove_participant_event_time'),
                    path('invite_list/', InviteListViewEventTime.as_view(), name="invite_list_event_time"),
                    path('update_participants/', UpdateParticipantsByEventTimeView.as_view(), name="update_participants_event_time"),
                    path('update_participants_directly/', UpdateParticipantsByEventTimeDirectlyView.as_view(), name="update_participants_event_time_directly"),
                    path('update_participants_info/', UpdateParticipantsInfoByEventTimeView.as_view(), name='update_participants_info_by_event_time'),
                    path('update_vip_info/', UpdateVipInfoByEventTimeView.as_view(), name='update_vip_info_by_event_time'),
                    path('send_email/', views.send_email_event_time, name="send_email_event_time"), # 從場次寄信給貴賓（單獨）
                    path('send_check_email/', views.send_check_email_event_time, name="send_check_email_event_time"), # 從場次寄確認信給貴賓（單獨）
                    path('send_remind_email/', views.send_remind_email_event_time, name="send_remind_email_event_time"), # 從場次寄提醒信給貴賓（單獨）
                    path('export_participants_event_time/', ExportParticipantsByEventTimeView.as_view(), name="export_participants_event_time"), # 從場次匯出貴賓名單
                    path('update_get_ticket_check/', views.update_get_ticket_check, name="update_get_ticket_check"), # 從場次更新貴賓是否已領票
                    path('update_seat_number/', views.update_seat_number, name="update_seat_number"), # 從場次更新貴賓座位號碼
                ])),
            ])),
            # path('participants/', include([ # 直接看專案的總表
            #     path('', ProjectParticipantsView.as_view(), name="project_participants"), # project_list/<int:project_id>/participants/
            #     path('<int:participant_id>/', include([   
            #         path('remove_participant/', views.remove_participant, name='remove_participant'), # project_list/<int:project_id>/participants/<int:participant_id>/remove_participant/
            #         path('send_email/', views.send_email, name="send_email"), # project_list/<int:project_id>/participants/<int:participant_id>/send_email/
            #     ])),
            # ])),
            # path('send_emails/', views.send_emails, name="send_emails"), # project_list/<int:project_id>/send_emails/
            
            path('update_participants/', views.update_participants, name="update_participants"), # project_list/<int:project_id>/update_participants/
            path('event_time/<int:event_time_id>/', include([
                path('invite_list/', InviteListViewEventTime.as_view(), name="invite_list_event_time"),
                path('send_emails_list/', SendEmailListViewEventTime.as_view(), name="send_emails_list_event_time"),
                
                path('send_emails/', views.send_emails_event_time, name="send_emails_event_time"),
                path('participants/', include([
                    # path('', ProjectParticipantsEventTimeView.as_view(), name="project_participants_event_time"),
                    path('<int:participant_id>/', include([
                        path('remove_participant/', views.remove_participant_event_time, name='remove_participant_event_time'),
                        
                    ])),
                ])),
            ])),
        ])),
    ])),
]