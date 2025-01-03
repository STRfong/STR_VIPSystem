from channels.generic.websocket import AsyncWebsocketConsumer
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

    async def send_update(self, event):
        # 只處理從 signal 來的更新
        await self.send(text_data=json.dumps({
            'type': 'vip_update',
            'action': event['action'],
            'participation': event['data'],
            'pp_id': event['pp_id'],
            'event_time_id': event['event_time_id']
        }))