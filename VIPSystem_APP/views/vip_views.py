from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView   
from django.db import models    
from VIPSystem_APP.models import VIP, Tag
from django.db.models import Count, Q
from django.urls import reverse_lazy
from VIPSystem_APP.forms import VIPForm
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages

@method_decorator(login_required, name='dispatch')
class VIPListView(ListView):
    model = VIP
    template_name = 'VIPSystem/vip_list.html'
    context_object_name = 'vip_list'
    paginate_by = 15  # 添加分页

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
            queryset = queryset.order_by('-project__count')
        elif sort_by_projects == 'false':
            queryset = queryset.order_by('project__count')
        else:
            queryset = queryset.order_by('name')

        return queryset

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
    
@login_required
def vip_create_from_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if excel_file:
            try:
                df = pd.read_excel(excel_file)
                created_count = 0
                for index, row in df.iterrows():
                    name = row.get('名稱') or row.get('中／英文本名')
                    if not name:
                        continue
                    
                    phone = str(row.get('電話號碼', '')).replace('_', '')
                    email = row.get('e-mail', '')
                    
                    VIP.objects.create(name=name, email=email, phone_number=phone)
                    created_count += 1
                
                messages.success(request, f'成功創建 {created_count} 個 VIP 記錄')
            except Exception as e:
                messages.error(request, f'處理 Excel 文件時出錯：{str(e)}')
            return redirect('VIPSystem_APP:vip_list')
    
    return render(request, 'VIPSystem/vip_create.html')