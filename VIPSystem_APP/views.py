from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404 # 例外處理
from django.db.models import Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import redirect
from .models import VIP, Project, Tag, ProjectParticipation
from .forms import VIPForm, ProjectForm
from django.template.loader import render_to_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from django.shortcuts import render
from django.db import models

@method_decorator(login_required, name='dispatch')
class VIPListView(ListView):
    model = VIP
    template_name = 'VIPSystem/vip_list.html'
    context_object_name = 'vip_list'
    paginate_by = 20  # 添加分页

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all()
        return context

    def get_queryset(self):
        queryset = VIP.objects.annotate(project__count=Count('project_participations', filter=models.Q(project_participations__status='confirmed')))
    
        # 處理標籤篩選
        tags = self.request.GET.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()
    
    # 處理排序
        sort_by_projects = self.request.GET.get('sort_by_projects')
        if sort_by_projects == 'true':
            return queryset.order_by('-project__count')
        elif sort_by_projects == 'false':
            return queryset.order_by('project__count')
        return queryset.order_by('name')

@method_decorator(login_required, name='dispatch')
class VIPDetailView(DetailView):
    model = VIP
    template_name = 'VIPSystem/vip_detail.html'   

@method_decorator(login_required, name='dispatch')
class VIPCreateView(CreateView):
    form_class = VIPForm        
    template_name = 'VIPSystem/vip_create.html'
    success_url = reverse_lazy('VIPSystem_APP:vip_list')

@method_decorator(login_required, name='dispatch')
class VIPUpdateView(UpdateView):
    form_class = VIPForm        
    template_name = 'VIPSystem/vip_create.html'
    queryset = VIP.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context

@method_decorator(login_required, name='dispatch')
class ProjectListView(ListView):
    model = Project
    template_name = 'VIPSystem/project_list.html'
    def get_queryset(self):
        return Project.objects.annotate(participants_count=Count('vip_participations'))

@method_decorator(login_required, name='dispatch')
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'VIPSystem/project_detail.html'
    context_object_name = 'project'

@method_decorator(login_required, name='dispatch')
class ProjectCreateView(CreateView):
    form_class = ProjectForm        
    template_name = 'VIPSystem/project_create.html'

@method_decorator(login_required, name='dispatch')
class ProjectUpdateView(UpdateView):
    form_class = ProjectForm        
    template_name = 'VIPSystem/project_create.html'
    queryset = Project.objects.all() # 這很重要

@method_decorator(require_http_methods(["DELETE"]), name='delete')
@method_decorator(login_required, name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    success_url = reverse_lazy('VIPSystem_APP:project_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        project_name = self.object.name
        self.object.delete()
        messages.success(request, f'專案 "{project_name}" 已成功刪除。')
        return JsonResponse({'status': 'success'})

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
def remove_participant(request, project_id, participant_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        participant = get_object_or_404(VIP, pk=participant_id)
        project_participation = get_object_or_404(ProjectParticipation, project=project, vip=participant)
        project_participation.delete()
        messages.success(request, f'已成功將 {participant.name} 從專案中移除。')
    return redirect('VIPSystem_APP:project_participants', pk=project_id)

# 信件相關

@login_required
def send_email(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        try:
            with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
                
                msg = MIMEMultipart('alternative')
                msg['From'] = "lab@strnetwork.cc"
                msg['To'] = request.POST['sender']
                msg['Subject'] = f"薩泰爾娛樂邀請您觀賞 《 {project.name} 》"
                
                # 渲染 HTML 模板
                html_content = render_to_string(
                    'VIPSystem/email_template.html',
                    {'username': request.user.username, 'content': request.POST['content']}
                )
                
                # 添加 HTML 内容到邮件
                msg.attach(MIMEText(html_content, 'html'))
                
                smtp.send_message(msg)
                print("完成!")
                messages.success(request, f"已成功發送邀請函給 {request.POST['sender']} !")
        except Exception as e:
            print("錯誤訊息: ", e)

        
        return redirect('VIPSystem_APP:project_participants', pk=project_id)
    return render(request, 'send_email.html')

@login_required
def send_emails(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        selected_vips = set(map(int, request.POST.getlist('selected_vips')))
        for vip_id in selected_vips:
            participation = ProjectParticipation.objects.get(id=vip_id)
            vip = VIP.objects.get(id=participation.vip.id)
            try:
                with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
                
                    msg = MIMEMultipart('alternative')
                    msg['From'] = "lab@strnetwork.cc"
                    msg['To'] = vip.email
                    msg['Subject'] = f"(多信件測試)薩泰爾娛樂邀請您觀賞 《 {project.name} 》"
                
                    html_content = render_to_string(
                        'VIPSystem/email_template.html',
                        {'username': request.user.username, 'content': request.POST['content']}
                    )
                    
                    msg.attach(MIMEText(html_content, 'html'))
                    
                    smtp.send_message(msg)
                    print("完成!")

                pp = ProjectParticipation.objects.get(project=project, vip=vip)
                pp.status = 'sended'
                pp.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})
            except Exception as e:
                print("錯誤訊息: ", e)
                # 替换 is_ajax() 检查
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e)})

        # 替换 is_ajax() 检查
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            messages.success(request, "所有邀請郵件已發送完成！")
            return redirect('VIPSystem_APP:project_participants', pk=project_id)
    return render(request, 'VIPSystem/send_emails.html', {'project': project})