"""
URL configuration for VIPSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from . import views
from .views import new_user_profile_profile_form, login_view
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', views.login_view, name='login'),
    path('VIPSystem_APP/', include('VIPSystem_APP.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('form/', TemplateView.as_view(template_name='form.html')),
    path('new_user_profile/', new_user_profile_profile_form, name='new_user_profile_profile_form'),
]