from django.db import models
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse # 新增
from allauth.socialaccount.models import SocialApp # type: ignore
from django.db import models
from django.contrib.sites.models import Site
import os

class CustomSocialApp(SocialApp):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        # 在保存之前，從環境變量中獲取值
        if self.provider == 'google':
            self.client_id = os.getenv('GOOGLE_CLIENT_ID', self.client_id)
            self.secret = os.getenv('GOOGLE_SECRET_KEY', self.secret)
        elif self.provider == 'facebook':
            self.client_id = os.getenv('FACEBOOK_CLIENT_ID', self.client_id)
            self.secret = os.getenv('FACEBOOK_SECRET_KEY', self.secret)
        # 添加其他社交平台的邏輯

        super().save(*args, **kwargs)

        try:
            current_site = Site.objects.get_current()
        except Site.DoesNotExist:
            current_site = Site.objects.create(domain='https://str-vipststem.zeabur.app/', name='https://str-vipststem.zeabur.app/')
        if current_site not in self.sites.all():
            self.sites.add(current_site)

    # @classmethod
    # def get_or_create_app(cls, provider):
    #     try:
    #         app = cls.objects.filter(provider=provider).first()  # 使用 .first() 而不是 .get()
    #         if not app:
    #             app = cls(provider=provider)
    #             app.name = f"{provider.capitalize()} OAuth"
    #             app.save()
    #         return app
    #     except Exception as e:
    #         print(f"Error in get_or_create_app: {str(e)}")
    #         return None 

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