from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ProjectParticipation
import json

@receiver([post_save, post_delete], sender=ProjectParticipation)
def notify_vip_update(sender, instance, created=False, **kwargs):
    try:
        channel_layer = get_channel_layer()
        event_time_id = instance.event_time.id

        # 判斷操作類型
        if kwargs['signal'] == post_delete:
            action = 'deleted'
            # 刪除時只發送必要的識別資訊
            message_data = {
                'pp_id': instance.pp_id,
                'vip_id': instance.vip.id
            }
        else:
            action = 'created' if created else 'updated'
            # 創建或更新時的完整資料
            message_data = {
                'pp_id': instance.pp_id,  # 將 pp_id 移到最前面以便查看
                'vip__name': instance.vip.name,
                'vip__id': instance.vip.id,
                'vip__nickname': instance.vip.nickname,
                'vip__organization': instance.vip.organization,
                'vip__position': instance.vip.position,
                'vip__phone_number': instance.vip.phone_number,
                'vip__email': instance.vip.email,
                'status': instance.get_status_display(),
                'invited_by__username': instance.invited_by.profile.nickname if instance.invited_by else '',
                'invited_by__email': instance.invited_by.email if instance.invited_by else '',
                'wish_attend': instance.wish_attend,
                'wish_attend_list': instance.get_wish_attend_list_ids(),
                'wish_ticket_count': instance.wish_ticket_count,
                'notes': instance.notes,
                'project_name': instance.project.name,
                'project_description': instance.project.description,
                'event_time_date': instance.event_time.date.strftime('%Y-%m-%d') if instance.event_time.date else '',
                'event_time_session': instance.event_time.session,
                'event_time_start_time': instance.event_time.start_time.strftime('%H:%M') if instance.event_time.start_time else '',
                'event_time_end_time': instance.event_time.end_time.strftime('%H:%M') if instance.event_time.end_time else '',
                'event_time_location_name': instance.event_time.location_name,
                'event_time_location_address': instance.event_time.location_address,
                'dead_line_date': instance.event_time.get_dead_line_weekday(),
                'event_time_format_date': instance.event_time.format_date_mm_dd(),
                'join_people_count': instance.join_people_count,
                'send_check_email': instance.send_check_email,
                'send_remind_email': instance.send_remind_email,
                'get_ticket_check': instance.get_ticket_check,
                'invited_at': instance.invited_at.strftime('%Y/%m/%d %H:%M') if instance.invited_at else '',
                'last_update_at': instance.last_update_at.strftime('%Y/%m/%d %H:%M') if instance.last_update_at else '',
                'seat_number': instance.seat_number,
            }

        # 發送更新消息
        async_to_sync(channel_layer.group_send)(
            f'vip_updates_{event_time_id}',
            {
                'type': 'send_update',
                'action': action,
                'data': message_data,
                'event_time_id': event_time_id,
                'pp_id': instance.pp_id  # 在頂層也添加 pp_id
            }
        )
    except Exception as e:
        print(f"WebSocket update error: {str(e)}")