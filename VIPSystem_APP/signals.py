from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ProjectParticipation
import json

@receiver([post_save, post_delete], sender=ProjectParticipation)
def notify_vip_update(sender, instance, **kwargs):
    try:
        channel_layer = get_channel_layer()
        event_time_id = instance.event_time.id

        # 獲取所有相關參與者資料
        participants = ProjectParticipation.objects.filter(
            event_time_id=event_time_id
        ).select_related('vip', 'invited_by')

        # 轉換為字典格式
        participants_data = [
            {
                'vip__name': p.vip.name,
                'vip__id': p.vip.id,
                'vip__nickname': p.vip.nickname,
                'vip__organization': p.vip.organization,
                'vip__position': p.vip.position,
                'vip__phone_number': p.vip.phone_number,
                'vip__email': p.vip.email,
                'status': p.get_status_display(),
                'invited_by__username': p.invited_by.profile.nickname if p.invited_by else '',
                'invited_by__email': p.invited_by.email if p.invited_by else '',
                'wish_attend': p.wish_attend,
                'wish_attend_list': p.get_wish_attend_list_ids(),
                'wish_ticket_count': p.wish_ticket_count,
                'notes': p.notes,
                'project_name': p.project.name,
                'project_description': p.project.description,
                'event_time_date': p.event_time.date.strftime('%Y-%m-%d') if p.event_time.date else '',
                'event_time_session': p.event_time.session,
                'event_time_start_time': p.event_time.start_time.strftime('%H:%M') if p.event_time.start_time else '',
                'event_time_end_time': p.event_time.end_time.strftime('%H:%M') if p.event_time.end_time else '',
                'event_time_location_name': p.event_time.location_name,
                'event_time_location_address': p.event_time.location_address,
                'dead_line_date': p.event_time.get_dead_line_weekday(),
                'event_time_format_date': p.event_time.format_date_mm_dd(),
                'pp_id': p.pp_id,
                'status': p.get_status_display(),
                'join_people_count': p.join_people_count,
                'send_check_email': p.send_check_email,
                'send_remind_email': p.send_remind_email,
                'get_ticket_check': p.get_ticket_check,
            }
            for p in participants
        ]

        # 發送更新消息
        async_to_sync(channel_layer.group_send)(
            f'vip_updates_{event_time_id}',
            {
                'type': 'send_update',
                'participants': participants_data
            }
        )
    except Exception as e:
        print(f"WebSocket update error: {str(e)}")