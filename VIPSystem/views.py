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
    
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from VIPSystem_APP.forms import StaffProfileForm
from VIPSystem_APP.models import StaffProfile
from django.contrib.auth.models import User
@login_required
def new_user_profile_profile_form(request):

    if hasattr(request.user, 'staffprofile'):
        return redirect('home')  # 如果已有 StaffProfile，直接重定向到首頁
    
    if request.method == 'POST':
        form = StaffProfileForm(request.POST)
        if form.is_valid():
            profile = User.objects.get(id=request.user.id).profile
            print(profile)
            print(form.cleaned_data)
            profile.phone_number = form.cleaned_data['phone_number']
            profile.department = form.cleaned_data['department']
            profile.save()
            return redirect('home')  # 或其他適當的頁面
    else:
        form = StaffProfileForm()
    
    return render(request, 'new_user_profile_profile_form.html', {'form': form})