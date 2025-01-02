from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ProjectParticipation
import json

class VIPUpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.event_time_id = self.scope['url_route']['kwargs']['event_time_id']
        self.room_group_name = f'vip_updates_{self.event_time_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'request_update':
            participants = await self.get_participants_data()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_update',
                    'participants': participants
                }
            )

    async def send_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'vip_update',
            'participants': event['participants']
        }))

    @database_sync_to_async
    def get_participants_data(self):
        participants = ProjectParticipation.objects.filter(
            event_time_id=self.event_time_id
        ).select_related('vip', 'invited_by')
        
        return [
            {
                'vip__name': p.vip.name,
                'vip__id': p.vip.id,
                'vip__nickname': p.vip.profile.nickname,
                'vip__organization': p.vip.organization,
                'vip__position': p.vip.position,
                'vip__phone_number': p.vip.phone_number,
                'vip__email': p.vip.email,
                'invited_by__username': p.invited_by.profile.nickname if p.invited_by else '',
                'invited_by__email': p.invited_by.email if p.invited_by else '',
                'wish_attend': p.wish_attend,
                'wish_attend_list': p.get_wish_attend_list_ids(),
                'wish_ticket_count': p.wish_ticket_count,
                'notes': p.notes,
                'project_name': p.project.name,
                'project_description': p.project.description,
                'event_time_date': p.event_time.date,
                'event_time_session': p.event_time.session,
                'event_time_start_time': p.event_time.start_time,
                'event_time_end_time': p.event_time.end_time,
                'event_time_location_name': p.event_time.location_name,
                'event_time_location_address': p.event_time.location_address,
                'dead_line_date': p.event_time.get_dead_line_weekday(),
                'event_time_format_date': p.event_time.format_date_mm_dd(),
                'pp_id': p.pp_id,
                'status': p.get_status_display(),
                'join_people_count': p.join_people_count,
                'send_check_email': p.send_check_email,
                'send_remind_email': p.send_remind_email,
            }
            for p in participants
        ]