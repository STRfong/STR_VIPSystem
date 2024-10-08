from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.shortcuts import redirect

@receiver(user_signed_up)
def redirect_to_profile_form(request, user, **kwargs):
    # 檢查是否是通過社交賬戶註冊的新用戶
    if 'sociallogin' in kwargs:
        # 檢查是否已經有 StaffProfile
        if not hasattr(user, 'staffprofile'):
            return redirect('new_user_profile_profile_form')