from django.views.generic import DetailView
from VIPSystem_APP.models import EventTime
from django.shortcuts import get_object_or_404

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
