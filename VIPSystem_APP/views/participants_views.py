from django.contrib.auth.decorators import login_required   
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from VIPSystem_APP.models import ProjectParticipation, VIP, Project, EventTime
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@method_decorator(login_required, name='dispatch')
class ProjectParticipantsView(ListView):
    model = ProjectParticipation
    template_name = 'VIPSystem/project_participants.html'
    context_object_name = 'participants_list'

    def get_queryset(self):
        project_id = self.kwargs.get('pk')
        return ProjectParticipation.objects.filter(project_id= project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('pk')
        context['project'] = get_object_or_404(Project, pk=project_id)
        return context
    
@method_decorator(login_required, name='dispatch')
class ProjectParticipantsEventTimeView(ListView):
    model = ProjectParticipation
    template_name = 'VIPSystem/project_participants_event_time.html'
    context_object_name = 'participants_list'

    def get_queryset(self):
        project_id = self.kwargs.get('pk')
        event_time_id = self.kwargs.get('event_time_id')
        return ProjectParticipation.objects.filter(project_id= project_id, event_time_id=event_time_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('pk')
        event_time_id = self.kwargs.get('event_time_id')
        context['project'] = get_object_or_404(Project, pk=project_id)
        context['event_time'] = get_object_or_404(EventTime, pk=event_time_id)
        return context
    
@method_decorator(login_required, name='dispatch') # 邀請貴賓參與專案
class InviteListView(ListView):
    model = VIP
    template_name = 'VIPSystem/invite_list.html'
    context_object_name = 'vip_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        context['project'] = project
        context['current_participants'] = project.participants.all()
        return context
    
@method_decorator(login_required, name='dispatch') # 邀請貴賓參與專案
class InviteListViewEventTime(ListView):
    model = VIP
    template_name = 'VIPSystem/invite_list_event_time.html'
    context_object_name = 'vip_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get('project_id')
        event_time_id = self.kwargs.get('event_time_id')
        project = get_object_or_404(Project, pk=project_id)
        context['project'] = project
        context['current_participants'] = project.participants.all()
        context['event_time'] = get_object_or_404(EventTime, pk=event_time_id)
        return context
    
@method_decorator(login_required, name='dispatch') # 發送邀請信
class SendEmailListView(ListView):
    model = ProjectParticipation
    template_name = 'VIPSystem/send_emails.html'
    context_object_name = 'vip_list'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return ProjectParticipation.objects.filter(project_id=project_id).exclude(status='confirmed')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('project_id'))
        return context
    
@method_decorator(login_required, name='dispatch') # 發送邀請信
class SendEmailListViewEventTime(ListView):
    model = ProjectParticipation
    template_name = 'VIPSystem/send_emails_event_time.html'
    context_object_name = 'vip_list'

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        event_time_id = self.kwargs.get('event_time_id')
        return ProjectParticipation.objects.filter(project_id=project_id, event_time_id=event_time_id).exclude(status='confirmed')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('project_id'))
        context['event_time'] = get_object_or_404(EventTime, pk=self.kwargs.get('event_time_id'))
        return context
    
@login_required
def update_participants(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        selected_vips = set(map(int, request.POST.getlist('selected_vips')))
        # 添加選中的VIP到參與者列表
        for vip_id in selected_vips:
            vip = VIP.objects.get(id=vip_id)
            ProjectParticipation.objects.update_or_create(
                project=project,
                vip=vip,
                invited_by=request.user,
                status = 'added'
            )
        
        return redirect('VIPSystem_APP:project_participants', pk=project.pk)
    
    # 如果不是POST請求，重定向回邀請列表頁面
    return redirect('VIPSystem_APP:invite_list', pk=project.pk)

@login_required
def update_participants_event_time(request, project_id, event_time_id):
    project = get_object_or_404(Project, id=project_id)
    event_time = get_object_or_404(EventTime, id=event_time_id)
    
    if request.method == 'POST':
        selected_vips = set(map(int, request.POST.getlist('selected_vips')))
        # 添加選中的VIP到參與者列表
        for vip_id in selected_vips:
            vip = VIP.objects.get(id=vip_id)
            ProjectParticipation.objects.update_or_create(
                project=project,
                vip=vip,
                invited_by=request.user,
                status = 'added',
                event_time=event_time
            )
        
        return redirect('VIPSystem_APP:project_participants_event_time', pk=project.pk, event_time_id=event_time.pk)
    
    # 如果不是POST請求，重定向回邀請列表頁面
    return redirect('VIPSystem_APP:invite_list_event_time', pk=project.pk, event_time_id=event_time.pk)

@login_required
def remove_participant(request, project_id, participant_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        participant = get_object_or_404(VIP, pk=participant_id)
        project_participation = get_object_or_404(ProjectParticipation, project=project, vip=participant)
        project_participation.delete()
        messages.success(request, f'已成功將 {participant.name} 從專案中移除。')
    return redirect('VIPSystem_APP:project_participants', pk=project_id)

@login_required
def remove_participant_event_time(request, project_id, event_time_id, participant_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        participant = get_object_or_404(VIP, pk=participant_id)
        project_participation = get_object_or_404(ProjectParticipation, project=project, vip=participant)
        project_participation.delete()
        messages.success(request, f'已成功將 {participant.name} 從專案中移除。')
    return redirect('VIPSystem_APP:project_participants_event_time', pk=project_id, event_time_id=event_time_id)