from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView   
from django.db import models    
from VIPSystem_APP.models import VIP, Tag
from django.db.models import Count, Q
from django.urls import reverse_lazy
from VIPSystem_APP.forms import VIPForm
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
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

        # 處理搜尋
        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

@method_decorator(login_required, name='dispatch')
class VIPDetailView(DetailView):
    model = VIP
    template_name = 'VIPSystem/vip_detail.html'
    pk_url_kwarg = 'vip_id'

@method_decorator(login_required, name='dispatch')
class VIPCreateView(CreateView):
    form_class = VIPForm        
    template_name = 'VIPSystem/vip_create.html'
    success_url = reverse_lazy('VIPSystem_APP:vip_list')
    pk_url_kwarg = 'vip_id'

@method_decorator(login_required, name='dispatch')
class VIPUpdateView(UpdateView):
    form_class = VIPForm        
    template_name = 'VIPSystem/vip_create.html'
    queryset = VIP.objects.all()
    pk_url_kwarg = 'vip_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
@method_decorator(require_http_methods(["DELETE"]), name='delete')
@method_decorator(login_required, name='dispatch')
class VIPDeleteView(DeleteView):
    model = VIP
    pk_url_kwarg = 'vip_id'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        vip_name = self.object.name
        self.object.delete()
        messages.success(self.request, f'已成功刪除貴賓 {vip_name}。')
        return JsonResponse({'status': 'success'})
    
@login_required
@require_http_methods(["GET", "POST"])
def vip_create_from_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        required_sheet_name = '貴賓名單'
        required_columns = [
            '中／英文本名', '稱呼／綽號', '貴賓性質', '單位', '職稱', 
            '電話號碼', 'e-mail', '貴賓聯絡人', '聯絡人職稱', 
            '聯絡人電話', '聯絡人信箱', 'STR 窗口', '備註', '收件地址'
        ]

        if excel_file:
            try:
                # 檢查工作表是否存在
                xl = pd.ExcelFile(excel_file)
                if required_sheet_name not in xl.sheet_names:
                    messages.error(request, f'Excel 檔案中找不到「{required_sheet_name}」工作表')
                    return redirect('VIPSystem_APP:vip_list')

                # 讀取指定工作表
                df = pd.read_excel(excel_file, sheet_name=required_sheet_name)
                
                # 檢查必要欄位
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(
                        request, 
                        f'工作表缺少以下必要欄位：{", ".join(missing_columns)}'
                    )
                    return redirect('VIPSystem_APP:vip_list')

                created_count = 0
                skipped_count = 0
                
                # Excel 欄位與 model 欄位的映射
                field_mapping = {
                    '中／英文本名': 'name',
                    '稱呼／綽號': 'nickname',
                    '單位': 'organization',
                    '職稱': 'position',
                    '電話號碼': 'phone_number',
                    'e-mail': 'email',
                    '貴賓聯絡人': 'poc',
                    '聯絡人職稱': 'poc_position',
                    '聯絡人電話': 'poc_phone_number',
                    '聯絡人信箱': 'poc_email',
                    'STR 窗口': 'str_connect',
                    '備註': 'notes',
                    '收件地址': 'address'
                }

                for index, row in df.iterrows():
                    # 檢查必填欄位
                    name = row.get('中／英文本名')
                    if not name:
                        continue
                    
                    # 處理 email（取第一個）
                    email_value = row.get('e-mail', '')
                    if pd.notna(email_value):
                        email = email_value.split(',')[0].strip()
                    else:
                        email = ''
                    
                    # 檢查重複
                    if VIP.objects.filter(name=name, email=email).exists():
                        skipped_count += 1
                        continue
                    
                    # 準備創建 VIP 的數據
                    vip_data = {}
                    for excel_field, model_field in field_mapping.items():
                        value = row.get(excel_field, '')
                        # 處理電話號碼格式
                        if 'phone' in model_field:
                            value = str(value).replace('_', '').strip() if pd.notna(value) else ''
                        # 處理 email 欄位
                        elif model_field == 'email':
                            value = email
                        # 處理其他可能的 NaN 值
                        elif pd.isna(value):
                            value = ''
                        vip_data[model_field] = value

                    # 創建 VIP 記錄
                    vip = VIP.objects.create(**vip_data)

                    # 處理貴賓性質（tags）
                    tags_str = row.get('貴賓性質', '')
                    if tags_str and pd.notna(tags_str):
                        # 先用逗號加空格分隔，然後對每個標籤執行 split("_")
                        tag_items = tags_str.split(", ")
                        for tag_item in tag_items:
                            if tag_item:
                                # 使用下劃線分割並取出必要資訊
                                tag_parts = tag_item.split("_")
                                if len(tag_parts) > 0:
                                    tag_name = tag_parts[1].strip()
                                    if tag_name:
                                        tag, _ = Tag.objects.get_or_create(name=tag_name)
                                        vip.tags.add(tag)

                    created_count += 1

                message = f'成功創建 {created_count} 個 VIP 記錄'
                if skipped_count > 0:
                    message += f'，跳過 {skipped_count} 個重複記錄'
                messages.success(request, message)
                
            except Exception as e:
                messages.error(request, f'處理 Excel 文件時出錯：{str(e)}')
            return redirect('VIPSystem_APP:vip_list')
    
    return render(request, 'VIPSystem/vip_create.html')

@method_decorator(login_required, name='dispatch')
class UpdateVipInfoByEventTimeView(LoginRequiredMixin, UpdateView):
    model = VIP

    def post(self, request, *args, **kwargs):
        vip_id = request.POST.get('vipId')
        vip = VIP.objects.get(id=vip_id)
        vip.name = request.POST.get('name')
        vip.nickname = request.POST.get('nickname')
        vip.organization = request.POST.get('organization')
        vip.position = request.POST.get('position')
        vip.phone_number = request.POST.get('phone_number')
        vip.email = request.POST.get('email')
        vip.save()
        project_id = kwargs['project_id']
        section = kwargs['section']
        event_time_id = kwargs['event_time_id'] 
        messages.success(request, f'{vip.name} 資訊已被更新')
        return redirect('VIPSystem_APP:participation_by_event_time', project_id=project_id, section=section, event_time_id=event_time_id)