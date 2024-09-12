from django.db import models
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse # 新增
from allauth.socialaccount.models import SocialApp # type: ignore
from django.db import models
from django.contrib.sites.models import Site
import os
from django.conf import settings
class CustomSocialApp(SocialApp):
    class Meta:
        proxy = True

    @classmethod
    def get_or_create_app(cls, provider):
        try:
            app, created = cls.objects.get_or_create(
                provider=provider,
                defaults={
                    'name': f"{provider.capitalize()} OAuth",
                    'client_id': os.getenv(f'{provider.upper()}_CLIENT_ID', ''),
                    'secret': os.getenv(f'{provider.upper()}_SECRET_KEY', ''),
                }
            )
            if created:
                current_site = Site.objects.get_current()
                app.sites.add(current_site)
            return app
        except Exception as e:
            print(f"Error in get_or_create_app: {str(e)}")
            return None

    def save(self, *args, **kwargs):
        if self.provider == 'google':
            self.client_id = os.getenv('GOOGLE_CLIENT_ID', self.client_id)
            self.secret = os.getenv('GOOGLE_SECRET_KEY', self.secret)
        elif self.provider == 'facebook':
            self.client_id = os.getenv('FACEBOOK_CLIENT_ID', self.client_id)
            self.secret = os.getenv('FACEBOOK_SECRET_KEY', self.secret)
        
        super().save(*args, **kwargs)

        current_site = Site.objects.get_current()
        if current_site not in self.sites.all():
            self.sites.add(current_site)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class VIP(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # 新增的字段
    tags = models.ManyToManyField(Tag, blank=True)  # 新增的字段

    def __str__(self):
        return self.name
    @property
    def project_count(self):
        return self.projects.count()
    
    def get_absolute_url(self):
        return reverse("VIPSystem_APP:vip_id", kwargs={"pk": self.pk})

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField(VIP, related_name='projects')
    # 其他Project相關欄位...

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("VIPSystem_APP:project_id", kwargs={"pk": self.pk})
    
    
@admin.register(VIP)
class VIPAdmin(admin.ModelAdmin):
    list_display = [field.name for field in VIP._meta.fields] + ['project_count']
    search_fields = ('name', 'email')

    def project_count(self, obj):
        return obj.projects__count
    project_count.admin_order_field = 'projects__count'
    project_count.short_description = '參與項目數'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(projects__count=Count('projects'))
        return queryset

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Project._meta.fields]
    search_fields = ('name','description')  # 在admin介面中，建立一個可以用來搜尋的介面； ('name','description')表示在搜尋的時候，可以搜尋name和description欄位