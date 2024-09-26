# -*- coding: utf-8 -*-
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
from VIPSystem_APP.models import ProjectParticipation, VIP, Project, EventTime
from email.header import Header
from collections import defaultdict
from datetime import date

@login_required
def send_email(request, project_id, participant_id):
    print(request.POST)
    project = get_object_or_404(Project, pk=project_id)
    vip = get_object_or_404(VIP, pk=participant_id)
    if request.method == 'POST':
        pp = ProjectParticipation.objects.get(project=project, vip=vip)
        random_token = get_random_string(length=32)
        email = Email(request.user.username, 
                        request.POST['sender'], 
                        request.POST.getlist('selected_event_times'), 
                        vip.name,
                        project, 
                        random_token)
        email.send_email()
        pp.token = random_token
        pp.status = 'sended'
        pp.save()
        messages.success(request, f"已成功發送邀請函給 {request.POST['sender']} !")
        return redirect('VIPSystem_APP:project_participants', project_id=project_id)
    return render(request, 'send_email.html')

@login_required
def send_email_event_time(request, project_id, event_time_id, participant_id):
    project = get_object_or_404(Project, pk=project_id)
    event_time = get_object_or_404(EventTime, pk=event_time_id)
    vip = get_object_or_404(VIP, pk=participant_id)
    if request.method == 'POST':
        pp = ProjectParticipation.objects.get(project=project, vip=vip, event_time=event_time)
        random_token = get_random_string(length=32)
        email = Email(request.user.username, 
                        request.POST['sender'], 
                        request.POST['content'], 
                        vip.name,
                        project, 
                        random_token)
        email.send_email()
        pp.token = random_token
        pp.status = 'sended'
        pp.save()
        messages.success(request, f"已成功發送邀請函給 {request.POST['sender']} !")
        return redirect('VIPSystem_APP:project_participants_event_time', project_id=project_id, event_time_id=event_time_id)
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
                          project, 
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

@login_required
def send_emails_event_time(request, project_id, event_time_id):
    project = get_object_or_404(Project, pk=project_id)
    event_time = get_object_or_404(EventTime, pk=event_time_id)
    if request.method == 'POST':
        selected_vips = set(map(int, request.POST.getlist('selected_vips')))
        for vip_id in selected_vips:
            participation = ProjectParticipation.objects.get(id=vip_id, event_time=event_time)
            vip = VIP.objects.get(id=participation.vip.id)
            try:
                pp = ProjectParticipation.objects.get(project=project, vip=vip)
                random_token = get_random_string(length=32)
                email = Email(request.user.username, 
                          vip.email, 
                          request.POST['content'], 
                          vip.name,
                          project, 
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
    def __init__(self, username, sender, selected_event_times_list, vip_name, project, token):
        self.username = username
        self.sender = sender
        self.selected_event_times_list = selected_event_times_list
        self.vip_name = vip_name
        self.project = project
        self.token = token

    def send_email(self):
         with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
                html_content = render_to_string(
                    'VIPSystem/email_template.html',
                    {'username': self.username, 
                     'selected_event_times': self.filter_selected_event_times(), 
                     'token': self.token, 
                     'vip_name': self.vip_name,
                     'project': self.project,
                     'SITE_URL': os.getenv('SITE_URL')}
                )
                
                # 添加 HTML 内容到邮件
                msg = MIMEText(html_content, 'html', 'utf-8')
                msg['From'] = Header("lab@strnetwork.cc",'utf-8')
                msg['To'] =  Header(self.sender,'utf-8')            
                subject = f" 【薩泰爾娛樂】《{self.project.name}》合作夥伴現場觀賞邀請"
                msg['Subject'] = Header(subject, 'utf-8')
                smtp.send_message(msg)  

    def filter_selected_event_times(self):
        selected_event_times = defaultdict(list)
        for event_time_id in self.selected_event_times_list:
            event_time = EventTime.objects.get(id=event_time_id)
            selected_event_times[event_time.location_name].append(event_time.date)
        formatted_result = self.format_date_list(selected_event_times)
        return formatted_result
    
    def format_date_list(self, selected_event_times):
        formatted_result = []
        for location, dates in selected_event_times.items():
            dates.sort()  # 確保日期是按順序排列的
            date_strings = []
            current_year = None
            current_month = None
            
            for i, d in enumerate(dates):
                if current_year != d.year:
                    date_strings.append(f"{d.year} 年 {d.month} 月 {d.day} 日")
                    current_year = d.year
                    current_month = d.month
                elif current_month != d.month:
                    if i > 0 and dates[i-1].year == d.year:
                        date_strings.append(f"{d.month} 月 {d.day} 日")
                    else:
                        date_strings.append(f"{d.year} 年 {d.month} 月 {d.day} 日")
                    current_month = d.month
                else:
                    date_strings.append(f"{d.day} 日")
            
            date_string = "、".join(date_strings)
            formatted_result.append(f"{date_string} 在 {location}")
        
        return formatted_result