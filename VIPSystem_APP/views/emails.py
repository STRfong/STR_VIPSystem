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
from datetime import datetime


@login_required
def send_email(request, project_id, participant_id):
    project = get_object_or_404(Project, pk=project_id)
    vip = get_object_or_404(VIP, pk=participant_id)
    if request.method == 'POST':
        pp = ProjectParticipation.objects.get(project=project, vip=vip)
        random_token = get_random_string(length=32)
        email = Email(request.user.username, 
                        request.POST['sender'], 
                        request.POST.getlist('selected_event_times'), 
                        pp.wish_ticket_count,
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

def send_email_by_section(request, project_id, section):
    project = get_object_or_404(Project, pk=project_id)
    vip = get_object_or_404(VIP, pk=request.POST['vip_id'])
    dead_line_date = request.POST['dead_line_date']
    if request.method == 'POST':
        pp = ProjectParticipation.objects.get(project=project, vip=vip)
        random_token = get_random_string(length=32)
        email = Email(request.user.username, 
                        request.POST['sender'], 
                        pp.get_wish_attend_list(), 
                        pp.wish_ticket_count,
                        vip.name,
                        project, 
                        dead_line_date,
                        random_token, 
                        request.POST['email_content'])
        email.send_email()
        pp.token = random_token
        pp.status = 'sended'
        pp.save()
        messages.success(request, f"已成功發送邀請函給 {request.POST['sender']} !")
        return redirect('VIPSystem_APP:participation_by_section', project_id=project_id, section=section)
    return render(request, 'send_email.html')

@login_required
def send_email_event_time(request, project_id, section, event_time_id):
    project = get_object_or_404(Project, pk=project_id)
    vip = get_object_or_404(VIP, pk=request.POST['vip_id'])
    event_time = get_object_or_404(EventTime, pk=event_time_id)
    dead_line_date = request.POST['dead_line_date']
    if request.method == 'POST':
        pp = get_object_or_404(ProjectParticipation, project=project, vip=vip)
        random_token = get_random_string(length=32)
        email = Email(request.user.username, 
                        request.POST['sender'], 
                        pp.get_wish_attend_list(), 
                        pp.wish_ticket_count,
                        vip.name,
                        project, 
                        event_time,
                        dead_line_date,
                        random_token, 
                        request.POST['email_content'])
        email.send_email()
        pp.token = random_token
        pp.status = 'sended'
        pp.save()
        messages.success(request, f"已成功發送邀請函給 {request.POST['sender']} !")
        return redirect('VIPSystem_APP:participation_by_event_time', project_id=project_id, section=section, event_time_id=event_time_id)
    return render(request, 'send_email.html')

@login_required
def send_emails(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        vip_id = request.POST.get('selected_vip')
        try:
            participation = ProjectParticipation.objects.get(id=vip_id)
            vip = VIP.objects.get(id=participation.vip.id)
            pp = ProjectParticipation.objects.get(project=project, vip=vip)
            random_token = get_random_string(length=32) 
            email = Email(request.user.username, 
                        vip.email, 
                        request.POST.getlist('selected_event_times'), 
                        pp.wish_ticket_count,
                        vip.name,
                        project, 
                        random_token) 
            email.send_email()        
            pp.token = random_token
            pp.status = 'sended'
            pp.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print("錯誤訊息: ", e)
            return JsonResponse({'status': 'error', 'message': str(e)})
        
    return render(request, 'VIPSystem/send_emails.html', {'project': project})

@login_required
def send_emails_event_time(request, project_id, event_time_id):
     if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        vip_id = request.POST.get('selected_vip')
        event_time = get_object_or_404(EventTime, pk=event_time_id)
        try:
            participation = ProjectParticipation.objects.get(id=vip_id, event_time=event_time)
            vip = VIP.objects.get(id=participation.vip.id)
            pp = ProjectParticipation.objects.get(project=project, vip=vip)
            random_token = get_random_string(length=32) 
            email = Email(request.user.username, 
                        vip.email, 
                        request.POST.getlist('selected_event_times'), 
                        pp.wish_ticket_count,
                        vip.name,
                        project, 
                        random_token) 
            email.send_email()        
            pp.token = random_token
            pp.status = 'sended'
            pp.event_time = event_time
            pp.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print("錯誤訊息: ", e)
            return JsonResponse({'status': 'error', 'message': str(e)})
        
@login_required
def send_emails_by_section(request, project_id, section):
    
    if request.method == 'POST':
        try:
            project = get_object_or_404(Project, pk=project_id)
            vip = get_object_or_404(VIP, pk=request.POST['selected_vip'])
            dead_line_date = request.POST['dead_line_date']
            pp = ProjectParticipation.objects.get(project=project, vip=vip)
            random_token = get_random_string(length=32)
            email = Email(request.user.username, 
                            vip.email, 
                            pp.get_wish_attend_list(), 
                            pp.wish_ticket_count,
                            vip.name,
                            project, 
                            dead_line_date,
                            random_token)
            email.send_email()        
            pp.token = random_token
            pp.status = 'sended'
            pp.save()
            if request.POST.get('done'):
                messages.success(request, f"已成功發送邀請函給 {request.POST.get('count')} 位合作夥伴 !")
            return JsonResponse({'status': 'success'})
        
        except Exception as e:
            print("錯誤訊息: ", e)
            return JsonResponse({'status': 'error', 'message': str(e)})

class Email():
    def __init__(self, username, sender, selected_event_times_list, wish_ticket_count, vip_name, project, event_time, dead_line_date, token, email_content):
        self.username = username
        self.sender = sender
        self.selected_event_times_list = selected_event_times_list
        self.wish_ticket_count = wish_ticket_count
        self.vip_name = vip_name
        self.project = project
        self.event_time = event_time
        self.dead_line_date = dead_line_date
        self.token = token
        self.email_content = email_content
    def send_email(self):
        with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
                html_content = render_to_string(
                    'VIPSystem/email_template.html',
                    {'username': self.username, 
                     'token': self.token, 
                     'vip_name': self.vip_name,
                     'wish_ticket_count': self.wish_ticket_count,
                     'project': self.project,
                     'dead_line_date': self.dead_line_date,
                     'event_time': self.event_time,
                     'SITE_URL': os.getenv('SITE_URL'),
                     'email_content': self.email_content}
                )
                
                # 添加 HTML 内容到邮件
                msg = MIMEText(html_content, 'html', 'utf-8')
                msg['From'] = Header("contact@strnetwork.cc",'utf-8')
                msg['To'] =  Header(self.sender,'utf-8')            
                subject = f" 【薩泰爾娛樂】【{self.project.name}】合作夥伴現場觀賞邀請"
                msg['Subject'] = Header(subject, 'utf-8')
                smtp.send_message(msg)  

    def get_weekday(self, date_string):
        date_object = datetime.strptime(date_string, "%Y年%m月%d日")
        weekday_number = date_object.weekday()
        days = ["一", "二", "三", "四", "五", "六", "日"]
        return f"{date_string}（{days[weekday_number]}）"
    
    @staticmethod # 新增於2024/12/17，用於篩選出不同地點的活動時間
    def filter_selected_event_location_name(selected_event_times_list):
        selected_event_session = defaultdict(list)
        for event_time in selected_event_times_list:
            selected_event_session[event_time.location_name].append(event_time.session)
        formatted_result = Email.format_location_name_list(selected_event_session)
        return formatted_result
    
    @staticmethod
    def format_location_name_list(selected_event_session):
        # 如果沒有資料，直接返回空列表
        if not selected_event_session:
            return []
        
        # 獲取所有地點
        locations = list(selected_event_session.keys())
        
        # # 獲取所有不重複的場次（從所有地點的場次中）
        # all_sessions = set()
        # for sessions in selected_event_session.values():
        #     all_sessions.update(sessions)
        # unique_sessions = sorted(all_sessions)  # 排序場次
        
        # 格式化地點字串
        if len(locations) == 1:
            location_str = f"在 {locations[0]}"
        elif len(locations) == 2:
            location_str = f"在 {locations[0]} 和 {locations[1]}"
        else:
            location_str = "在 " + "、".join(locations[:-1]) + "、和" + locations[-1]
        
        # # 格式化場次字串
        # session_str = "、".join(unique_sessions)
        
        # 組合最終結果
        formatted_result = f"{location_str}" # 舉辦 {session_str}"
        return formatted_result


    @staticmethod 
    def filter_selected_event_times(selected_event_times_list):
        selected_event_times = defaultdict(list)
        for event_time in selected_event_times_list:
            selected_event_times[event_time.location_name].append(event_time.date)
        formatted_result = Email.format_date_list(selected_event_times)
        return formatted_result
    
    @staticmethod
    def format_date_list(selected_event_times):
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
    

def handle_invitation_response(request, token):
    if request.method == 'POST':
        response = request.POST.get('response')
        join_people_count = int(request.POST.get('join_people_count') or 0)
        notes = request.POST.get('notes')
        event_time_id = request.POST.get('eventTime')
        participation = get_object_or_404(ProjectParticipation, token=token)
        participation.handle_response(response, join_people_count, event_time_id, notes)
        return render(request, 'VIPSystem/thank_you_page.html')



    participation = get_object_or_404(ProjectParticipation, token=token)
    project = participation.project
    selected_event_times_list = participation.get_wish_attend_list()
    context = {
        'participation': participation,
        'project': project,
        'selected_event_times': Email.filter_selected_event_times(selected_event_times_list),
        'selected_event_location_name': Email.filter_selected_event_location_name(selected_event_times_list)
    }
    return render(request, 'VIPSystem/form.html', context)  # 創建一個感謝頁面