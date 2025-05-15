# medsafe/consumer.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"user_{self.user.id}"

        # 유저 ID 기반 그룹에 가입
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # 서버에서 보낸 메시지를 클라이언트에 전달
    async def prescription_done(self, event):
        await self.send(text_data=json.dumps({
            "type": "prescription.done",
            "message": event["message"],
            "prescription_id": event["prescription_id"],
            "medications": event.get("medications", [])
        }))
