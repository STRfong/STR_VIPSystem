from django.contrib import admin

# Register your models here.

from .models import VIP, Project, Tag, CustomSocialApp
from allauth.socialaccount.admin import SocialAppAdmin # type: ignore
from allauth.socialaccount.models import SocialApp # type: ignore

admin.site.register(Tag)
admin.site.unregister(SocialApp)
admin.site.register(CustomSocialApp, SocialAppAdmin)