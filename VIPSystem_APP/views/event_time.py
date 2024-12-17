from django.views.generic import DetailView, CreateView, UpdateView, ListView, DeleteView
from VIPSystem_APP.models import EventTime, Project
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View


class EventTimeDetailView(DetailView):
    model = EventTime
    template_name = 'VIPSystem/event_time_detail.html'
    context_object_name = 'event_time'

    def get_object(self):
        return get_object_or_404(
            EventTime,
            project__id=self.kwargs['project_id'],
            id=self.kwargs['event_time_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.object.project
        confirmed_participants = self.object.project.vip_participations.filter(
            project=self.object.project,
            event_time=self.object,
            status='confirmed'
        )
        context['confirmed_participant_count'] = sum(participant.join_people_count for participant in confirmed_participants)
        return context

@method_decorator(login_required, name='dispatch')
class EventTimeCreateView(CreateView):
    def post(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        project = Project.objects.get(pk=project_id)
        event_time = EventTime(
            project=project,
            date=request.POST.get('date'),
            entry_time=request.POST.get('entry_time'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            section=request.POST.get('section'),
            session=request.POST.get('session'),
            location_name=request.POST.get('location_name'),
            location_address=request.POST.get('location_address'),
            ticket_count=request.POST.get('ticket_count'),
            dead_line_date=request.POST.get('dead_line_date'),
            dispatch_date=request.POST.get('dispatch_date'),
            announce_date=request.POST.get('announce_date')
        )
        event_time.save()
        # messages.success(request, f'場次 {event_time.date} {event_time.section} {event_time.get_session_display()}已成功新增。')
        messages.success(request, f'場次 {event_time.date} {event_time.section} {event_time.session}已成功新增。')
        return redirect('VIPSystem_APP:project_detail', project_id=project_id)

@method_decorator(login_required, name='dispatch')
class UpdateEventTimeView(UpdateView):    
    def post(self, request, *args, **kwargs):
        event_time_id = request.POST.get('event_time_id')
        event_time = get_object_or_404(EventTime, pk=event_time_id)
        event_time.date = request.POST.get('date')
        event_time.entry_time = request.POST.get('entry_time')
        event_time.start_time = request.POST.get('start_time')
        event_time.end_time = request.POST.get('end_time')
        event_time.section = request.POST.get('section')
        event_time.session = request.POST.get('session')
        event_time.location_name = request.POST.get('location_name')
        event_time.location_address = request.POST.get('location_address')
        event_time.ticket_count = request.POST.get('ticket_count')
        event_time.dead_line_date = request.POST.get('dead_line_date')
        event_time.dispatch_date = request.POST.get('dispatch_date')
        event_time.announce_date = request.POST.get('announce_date')
        event_time.save()
        # messages.success(request, f'場次 {event_time.date} {event_time.section} {event_time.get_session_display()}已成功更新。')
        messages.success(request, f'場次 {event_time.date} {event_time.section} {event_time.session}已成功更新。')
        return redirect('VIPSystem_APP:project_detail', project_id=event_time.project.id)



@method_decorator(login_required, name='dispatch')
class DeleteEventTimeView(DeleteView):
    def post(self, request, *args, **kwargs):
        event_time_id = request.POST.get('event_time_id')
        event_time = get_object_or_404(EventTime, pk=event_time_id)
        event_time.delete()
        # messages.success(request, f'場次 {event_time.date} {event_time.section} {event_time.get_session_display()}已成功刪除。')
        messages.success(request, f'場次 {event_time.date} {event_time.section} {event_time.session}已成功刪除。')
        return redirect('VIPSystem_APP:project_detail', project_id=event_time.project.id)
