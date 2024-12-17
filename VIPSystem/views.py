from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from VIPSystem_APP.forms import StaffProfileForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
def login_view(request):
    # 如果用戶已經登入，直接重定向到首頁
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # 先用 email 找到對應的用戶
            user = User.objects.get(email=email)
            # 使用用戶名和密碼進行驗證
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                # 獲取 next 參數，如果沒有就導向首頁
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, '密碼錯誤')
        except User.DoesNotExist:
            messages.error(request, '找不到此電子信箱的帳號')
        
        return render(request, 'account/login.html')
    
    return render(request, 'account/login.html')

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
    

@login_required
def new_user_profile_profile_form(request):

    if hasattr(request.user, 'staffprofile'):
        return redirect('home')  # 如果已有 StaffProfile，直接重定向到首頁
    
    if request.method == 'POST':
        form = StaffProfileForm(request.POST)
        if form.is_valid():
            profile = User.objects.get(id=request.user.id).profile
            profile.phone_number = form.cleaned_data['phone_number']
            profile.department = form.cleaned_data['department']
            profile.save()
            return redirect('home')  # 或其他適當的頁面
    else:
        form = StaffProfileForm()
    
    return render(request, 'new_user_profile_profile_form.html', {'form': form})