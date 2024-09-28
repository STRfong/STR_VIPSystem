from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView   
from django.db.models import Count, Q
from django.urls import reverse_lazy
from VIPSystem_APP.models import Project, EventTime 
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from VIPSystem_APP.forms import ProjectForm, EventTimeFormSet
from django.shortcuts import redirect

@method_decorator(login_required, name='dispatch')
class ProjectListView(ListView):
    model = Project
    template_name = 'VIPSystem/project_list.html'
    pk_url_kwarg = 'project_id'

    def get_queryset(self):
        return Project.objects.annotate(participants_count=Count('vip_participations'))

@method_decorator(login_required, name='dispatch')
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'VIPSystem/project_detail.html'
    context_object_name = 'project'
    pk_url_kwarg = 'project_id'

@method_decorator(login_required, name='dispatch')
class ProjectCreateView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        project_form = ProjectForm(request.POST)
        event_time_data = {
            'form-TOTAL_FORMS': str(len(request.POST.getlist('event_date'))),
            'form-INITIAL_FORMS': '0',
            'form-MAX_NUM_FORMS': '',
        }
        try:
            for i, date in enumerate(request.POST.getlist('event_date')):
                event_time_data.update({
                f'form-{i}-event_date': date,
                f'form-{i}-event_time': request.POST.getlist('event_time')[i],
                f'form-{i}-event_end_time': request.POST.getlist('event_end_time')[i],
                f'form-{i}-event_session': request.POST.getlist('event_session')[i],
                f'form-{i}-ticket_count': request.POST.getlist('ticket_count')[i],
                f'form-{i}-event_location': request.POST.getlist('event_location')[i],
                f'form-{i}-event_address': request.POST.getlist('event_address')[i],
            })
        except Exception as e:
            messages.error(request, f'專案建立失敗，請檢查輸入資料是否正確。{e}')
            print(e)
            return redirect('VIPSystem_APP:project_list')
        try:
            event_time_formset = EventTimeFormSet(event_time_data)

            if project_form.is_valid() and event_time_formset.is_valid():
                project = project_form.save()
                event_times = []
                for form in event_time_formset:
                    event_time = EventTime(
                        project=project,
                        date=form.cleaned_data['event_date'],
                        start_time=form.cleaned_data['event_time'],
                        end_time=form.cleaned_data['event_end_time'],
                        session=form.cleaned_data['event_session'],
                        location_name=form.cleaned_data['event_location'],
                        location_address=form.cleaned_data['event_address'],
                        ticket_count=form.cleaned_data['ticket_count']
                    )
                    event_times.append(event_time)              

                EventTime.objects.bulk_create(event_times)
                messages.success(request, f'專案《{project.name}》已成功建立，共 {len(event_times)} 場次。')
                return redirect('VIPSystem_APP:project_list')
        except Exception as e:
            print(e)
            messages.error(request, f'專案建立失敗，請檢查輸入資料是否正確。{e}')
            return redirect('VIPSystem_APP:project_list')

        else:
            messages.error(request, '專案建立失敗，請檢查輸入資料是否正確。')
            return redirect('VIPSystem_APP:project_list')
    

@method_decorator(login_required, name='dispatch')
class ProjectUpdateView(UpdateView):
    # form_class = ProjectForm        
    template_name = 'VIPSystem/project_create.html'
    queryset = Project.objects.all() # 這很重要

@method_decorator(require_http_methods(["DELETE"]), name='delete')
@method_decorator(login_required, name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    pk_url_kwarg = 'project_id'
    success_url = reverse_lazy('VIPSystem_APP:project_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        project_name = self.object.name
        self.object.delete()
        messages.success(request, f'專案 "{project_name}" 已成功刪除。')
        return JsonResponse({'status': 'success'})
