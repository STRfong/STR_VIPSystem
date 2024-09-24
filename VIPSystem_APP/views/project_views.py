from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView   
from django.db.models import Count, Q
from django.urls import reverse_lazy
from VIPSystem_APP.models import Project
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages

@method_decorator(login_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProjectListView(ListView):
    model = Project
    template_name = 'VIPSystem/project_list.html'
    def get_queryset(self):
        return Project.objects.annotate(participants_count=Count('vip_participations'))

@method_decorator(login_required, name='dispatch')
class ProjectDetailView(DetailView):
    model = Project
    template_name = 'VIPSystem/project_detail.html'
    context_object_name = 'project'

@method_decorator(login_required, name='dispatch')
class ProjectCreateView(CreateView):
    # form_class = ProjectForm        
    template_name = 'VIPSystem/project_create.html'

@method_decorator(login_required, name='dispatch')
class ProjectUpdateView(UpdateView):
    # form_class = ProjectForm        
    template_name = 'VIPSystem/project_create.html'
    queryset = Project.objects.all() # 這很重要

@method_decorator(require_http_methods(["DELETE"]), name='delete')
@method_decorator(login_required, name='dispatch')
class ProjectDeleteView(DeleteView):
    model = Project
    success_url = reverse_lazy('VIPSystem_APP:project_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        project_name = self.object.name
        self.object.delete()
        messages.success(request, f'專案 "{project_name}" 已成功刪除。')
        return JsonResponse({'status': 'success'})
