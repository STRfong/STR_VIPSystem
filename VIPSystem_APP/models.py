from django.db import models
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse # 新增
from django.db import models
from django.utils.timezone import now
from django.utils.formats import date_format
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department_choices = [
        ('@operation', '營運部'),
        ('@lab', '服務科學實驗室'),
        ('@ceoo', '執行長室'),
        ('@bd', '商業開發事業部'),
        ('@burn', '炎上'),
        ('@tnns', '夜夜秀'),
        ('@showcase', '拼盤秀'),
        ('@stream', '串流'),
        ('@agency', '藝人經紀'),
        ('@so', '社群'),
        ('@showdev', '節目開發'),
    ]
    department = models.CharField(max_length=100, choices=department_choices, blank=True, null=True)

    def __str__(self):
        return self.user.username       
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            StaffProfile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

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
    entry_time = models.TimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    section = models.CharField(max_length=100)
    session_choices = [
        ('morning', '早場'),
        ('afternoon', '午場'),
        ('evening', '晚場'),
    ]
    session = models.CharField(max_length=10, choices=session_choices)
    location_name = models.CharField(max_length=100)
    location_address = models.CharField(max_length=200)
    ticket_count = models.IntegerField()
    dead_line_date = models.DateField()
    dispatch_date = models.DateField()
    announce_date = models.DateField()

    def __str__(self):
         return f"{date_format(self.date, 'Y/m/d')} {self.get_session_display()}"
    
    def get_weekday(self):
        weekday_number = self.dead_line_date.weekday()
        days = ["一", "二", "三", "四", "五", "六", "日"]
        return f"{self.dead_line_date}（{days[weekday_number]}）"
    
    def total_join_people_count(self):
        return self.participations.aggregate(total=models.Sum('join_people_count'))['total'] or 0
    
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
    last_update_at = models.DateTimeField(auto_now=True)
    event_time = models.ForeignKey(EventTime, on_delete=models.SET_NULL, null=True, blank=True, related_name='participations')
    join_people_count = models.IntegerField(default=0)
    token = models.CharField(max_length=100, unique=True, null=True, blank=True)
    wish_attend = models.CharField(max_length=50, blank=True, default='都可以')
    wish_attend_section = models.CharField(max_length=50, blank=True, default='台灣')

    def handle_response(self, response, join_people_count, event_time_id):
        if response == 'confirmed':
            self.status = 'confirmed'
            self.join_people_count = join_people_count
            self.event_time = EventTime.objects.get(id=event_time_id)
        elif response == 'declined':
            self.status = 'declined'
        
        self.token = None  # 使令牌失效
        self.save()

    def get_wish_attend_list(self):
        if 'all' in self.wish_attend:
            return EventTime.objects.filter(project=self.project, section=self.wish_attend_section)
        else:
            return [EventTime.objects.get(id=event_time_id) for event_time_id in self.wish_attend.split(',') if event_time_id.strip()]
        
    def wish_attend_list_email(self):
        from .views.emails import Email
        return Email.filter_selected_event_times(self.get_wish_attend_list())
    
    def get_dead_line_date(self):
        date_list = [event.dead_line_date for event in self.get_wish_attend_list()]
        return min(date_list)

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

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StaffProfile._meta.fields]
    search_fields = ('user__username', 'phone_number', 'department')
    list_filter = ('department',)
    list_per_page = 10
    list_max_show_all = 100
    
