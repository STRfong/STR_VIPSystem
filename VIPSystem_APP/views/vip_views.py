from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView   
from django.db import models    
from VIPSystem_APP.models import VIP, Tag
from django.db.models import Count, Q
from django.urls import reverse_lazy
from VIPSystem_APP.forms import VIPForm

@method_decorator(login_required, name='dispatch')
class VIPListView(ListView):
    model = VIP
    template_name = 'VIPSystem/vip_list.html'
    context_object_name = 'vip_list'
    paginate_by = 20  # 添加分页

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_tags'] = Tag.objects.all()
        return context

    def get_queryset(self):
        queryset = VIP.objects.annotate(project__count=Count('project_participations', filter=models.Q(project_participations__status='confirmed')))
    
        # 處理標籤篩選
        tags = self.request.GET.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()
    
    # 處理排序
        sort_by_projects = self.request.GET.get('sort_by_projects')
        if sort_by_projects == 'true':
            return queryset.order_by('-project__count')
        elif sort_by_projects == 'false':
            return queryset.order_by('project__count')
        return queryset.order_by('name')

@method_decorator(login_required, name='dispatch')
class VIPDetailView(DetailView):
    model = VIP
    template_name = 'VIPSystem/vip_detail.html'   

@method_decorator(login_required, name='dispatch')
class VIPCreateView(CreateView):
    form_class = VIPForm        
    template_name = 'VIPSystem/vip_create.html'
    success_url = reverse_lazy('VIPSystem_APP:vip_list')

@method_decorator(login_required, name='dispatch')
class VIPUpdateView(UpdateView):
    form_class = VIPForm        
    template_name = 'VIPSystem/vip_create.html'
    queryset = VIP.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context