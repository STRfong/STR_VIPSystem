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
        return reverse("VIPSystem_APP:vip_detail", kwargs={"vip_id": self.pk})

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    participants = models.ManyToManyField(VIP, through='ProjectParticipation', related_name='projects')

    def __str__(self):
        return self.name
    @property
    def all_ticket_count(self):
        return sum(event_time.ticket_count for event_time in self.event_times.all())

    def get_absolute_url(self):
        return reverse("VIPSystem_APP:project_detail", kwargs={"project_id": self.pk})
    
class EventTime(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='event_times')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    session_choices = [
        ('morning', '早場'),
        ('afternoon', '午場'),
        ('evening', '晚場'),
    ]
    session = models.CharField(max_length=10, choices=session_choices)
    location_name = models.CharField(max_length=100)
    location_address = models.CharField(max_length=200)
    ticket_count = models.IntegerField()

    def __str__(self):
        return f"{self.project.name} - {self.date} - {self.get_session_display()}"
    
class ProjectParticipation(models.Model):
    vip = models.ForeignKey(VIP, on_delete=models.CASCADE, related_name='project_participations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='vip_participations')
    invited_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='invitations')
    status = models.CharField(max_length=20, choices=[
        ('added', '已新增尚未寄信'),
        ('confirmed', '確認參加'),
        ('sended', '已發送邀請信件等待回覆'),
        ('declined', '拒絕參加'),
    ], default='added')
    invited_at = models.DateTimeField(auto_now_add=True)
    event_time = models.ForeignKey(EventTime, on_delete=models.SET_NULL, null=True, blank=True, related_name='participations')
    join_people_count = models.IntegerField(default=0)
    token = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def handle_response(self, response, join_people_count, event_time_id):
        if response == 'confirmed':
            self.status = 'confirmed'
            self.join_people_count = join_people_count
            self.event_time = EventTime.objects.get(id=event_time_id)
        elif response == 'declined':
            self.status = 'declined'
        
        self.token = None  # 使令牌失效
        self.save()

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

@admin.register(EventTime)
class EventTimeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in EventTime._meta.fields]
    search_fields = ('project__name', 'date', 'time', 'session', 'location', 'ticket_count')
    list_filter = ('session',)
    list_editable = ('ticket_count',)
    list_per_page = 10
    list_max_show_all = 100
    