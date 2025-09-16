# from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class ProjectConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # lazy import to avoid AppRegistryNotReady
        from django.contrib.auth.models import AnonymousUser
        from .models import Membership

        user = self.scope.get("user", AnonymousUser())
        if not user or user.is_anonymous:
            await self.close(code=4001)
            return

        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]

        # DB check in thread
        is_member = await database_sync_to_async(
            lambda: Membership.objects.filter(
                user=user,
                organization__projects__id=self.project_id
            ).exists()
        )()

        if not is_member:
            await self.close(code=4003)
            return

        self.group_name = f"project_{self.project_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()


    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def issue_created(self, event):
        await self.send_json({
            "type": "issue.created",
            "issue_id": event.get("issue_id"),
            "title": event.get("title")
        })

    async def issue_updated(self, event):
        await self.send_json({
            "type": "issue.updated",
            **event
        })

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "Connected to notifications ✅"
        }))

    async def disconnect(self, close_code):
        # Disconnect logic
        pass