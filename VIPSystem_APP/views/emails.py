# -*- coding: utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
import smtplib
import os
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from VIPSystem_APP.models import ProjectParticipation, VIP, Project
from email.header import Header

@login_required
def send_email(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    vip = VIP.objects.get(id=request.POST['vip_id'])
    if request.method == 'POST':
        try:
            pp = ProjectParticipation.objects.get(project=project, vip=vip)
            random_token = get_random_string(length=32)
            email = Email(request.user.username, 
                          request.POST['sender'], 
                          request.POST['content'], 
                          vip.name,
                          project.name, 
                          random_token)
            email.send_email()        
            pp.token = random_token
            pp.status = 'sended'
            pp.save()
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
                pp = ProjectParticipation.objects.get(project=project, vip=vip)
                random_token = get_random_string(length=32)
                email = Email(request.user.username, 
                          vip.email, 
                          request.POST['content'], 
                          vip.name,
                          project.name, 
                          random_token)
                email.send_email()        
                pp.token = random_token
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

def handle_invitation_response(request, token):
    participation = get_object_or_404(ProjectParticipation, token=token)
    response = request.GET.get('response')
    participation.handle_response(response)
    return render(request, 'VIPSystem/thank_you_page.html')  # 創建一個感謝頁面

class Email():
    def __init__(self, username, sender, content, vip_name, project_name, token):
        self.username = username
        self.sender = sender
        self.content = content
        self.vip_name = vip_name
        self.project_name = project_name
        self.token = token

    def send_email(self):
         with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
                
                
                msg = MIMEMultipart('alternative')
                msg['From'] = Header("lab@strnetwork.cc",'utf-8')
                msg['To'] =  Header(self.sender,'utf-8')
                subject = f" 【薩泰爾娛樂】《{self.project_name}》合作夥伴現場觀賞邀請"
                msg['Subject'] = Header(subject, 'utf-8')
                # 渲染 HTML 模板
                html_content = render_to_string(
                    'VIPSystem/email_template.html',
                    {'username': self.username, 
                     'content': self.content, 
                     'token': self.token, 
                     'vip_name': self.vip_name,
                     'project_name': self.project_name,
                     'SITE_URL': os.getenv('SITE_URL')}
                )
                
                # 添加 HTML 内容到邮件
                msg.attach(MIMEText(html_content, 'html', 'utf-8'))
                smtp.send_message(msg)

# <a href="{{ SITE_URL }}{% url 'VIPSystem_APP:respond' token %}?response=yes" class="button accept">接受邀請</a>
# <a href="{{ SITE_URL }}{% url 'VIPSystem_APP:respond' token %}?response=no" class="button decline">婉拒邀請</a>