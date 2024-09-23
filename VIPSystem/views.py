from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from django.template.loader import render_to_string

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print("Errors", form.errors)
        if form.is_valid():
            form.save()
            return redirect('/')
        else:
            return render(request, 'registration/register.html', {'form':form})
    else:
        form = UserCreationForm()
        context = {'form': form}
        return render(request, 'registration/register.html', context)


def send_email(request):
    if request.method == 'POST':
        try:
            with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(os.getenv('EMAIL_HOST_USER'), os.getenv('EMAIL_HOST_PASSWORD'))
                
                msg = MIMEMultipart('alternative')
                msg['From'] = "lab@strnetwork.cc"
                msg['To'] = request.POST['sender']
                msg['Subject'] = "測試郵件"
                
                # 渲染 HTML 模板
                html_content = render_to_string(
                    'email_template.html',
                    {'username': request.user.username, 'content': request.POST['content']}
                )
                
                # 添加 HTML 内容到邮件
                msg.attach(MIMEText(html_content, 'html'))
                
                smtp.send_message(msg)
                print("完成!")
        except Exception as e:
            print("錯誤訊息: ", e)
        
        return redirect('/')
    return render(request, 'send_email.html')