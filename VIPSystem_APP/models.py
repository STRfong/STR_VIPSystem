from django.db import models
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse # 新增
from django.db import models

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
        return self.project_participations.count() # 獲取參與數量
    
    def get_absolute_url(self):
        return reverse("VIPSystem_APP:vip_id", kwargs={"pk": self.pk})

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    participants = models.ManyToManyField(VIP, through='ProjectParticipation', related_name='projects')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("VIPSystem_APP:project_id", kwargs={"pk": self.pk})
    
class ProjectParticipation(models.Model):
    vip = models.ForeignKey(VIP, on_delete=models.CASCADE, related_name='project_participations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='vip_participations')
    invited_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='invitations')
    status = models.CharField(max_length=20, choices=[
        ('pending', '等待回覆'),
        ('confirmed', '確認參加'),
    ], default='pending')
    invited_at = models.DateTimeField(auto_now_add=True)

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

@admin.register(ProjectParticipation)
class ProjectParticipationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProjectParticipation._meta.fields]
    search_fields = ('project__name', 'vip__name')
    list_filter = ('status',)
    list_editable = ('status',)
    list_per_page = 10
    list_max_show_all = 100
    