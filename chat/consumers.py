import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from django.contrib.auth.models import User
from .models import Message, UserActivity


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        query_params = parse_qs(self.scope['query_string'].decode())
        self.username = query_params.get('username', ['Anonymous'])[0]
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        if not hasattr(self.channel_layer, 'online_users'):
            self.channel_layer.online_users = {}
        self.channel_layer.online_users.setdefault(self.room_group_name, set()).add(self.username)

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.username,
                'online_users': list(self.channel_layer.online_users[self.room_group_name]),
                'all_users': await self.get_all_users()
            }
        )

        messages = await self.get_previous_messages()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': msg['content'],
                'username': msg['username'],
                'timestamp': msg['timestamp'],
            }))

    async def disconnect(self, close_code):
        if self.room_group_name in getattr(self.channel_layer, 'online_users', {}):
            self.channel_layer.online_users[self.room_group_name].discard(self.username)

        await self.save_last_seen()

        last_seen = await self.get_last_seen(self.username)

        # ✅ Send offline notification
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'offline_notification',
                'message': f'{self.username} has gone offline.'
            }
        )

        # ✅ Send user_leave update
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'username': self.username,
                'online_users': list(self.channel_layer.online_users.get(self.room_group_name, [])),
                'last_seen': last_seen,
                'all_users': await self.get_all_users()
            }
        )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if 'message' in data:
            message = data['message'].strip()
            if message:
                await self.save_message(self.username, self.room_name, message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': self.username,
                        'timestamp': now().strftime('%Y-%m-%d %H:%M:%S'),
                    }
                )

                # ✅ Send offline notification for other users who are offline
                other_users = self.get_other_usernames(self.username)
                for user in other_users:
                    if user not in self.channel_layer.online_users.get(self.room_group_name, set()):
                        await self.send(text_data=json.dumps({
                            'type': 'offline_notification',
                            'message': f"{user} is offline. Your message will be delivered when they're back."
                        }))

        elif 'typing' in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': self.username,
                    'typing': data['typing']
                }
            )

    def get_other_usernames(self, current_user):
        try:
            name1, name2 = self.room_name.split("_")
            return [name for name in [name1, name2] if name != current_user]
        except:
            return []

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
            'online_users': event['online_users'],
            'all_users': event['all_users'],
            'message': f"{event['username']} joined the chat"
        }))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username'],
            'online_users': event['online_users'],
            'all_users': event['all_users'],
            'last_seen': event['last_seen'],
            'message': f"{event['username']} left the chat"
        }))

    async def typing_indicator(self, event):
        if event['username'] != self.username:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'typing': event['typing'],
            }))

    async def offline_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offline_notification',
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, username, room, message):
        return Message.objects.create(username=username, room=room, content=message)

    @database_sync_to_async
    def get_previous_messages(self):
        msgs = Message.objects.filter(room=self.room_name).order_by('-timestamp')[:25]
        return list(reversed([{
            'username': m.username,
            'content': m.content,
            'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for m in msgs]))

    @database_sync_to_async
    def save_last_seen(self):
        UserActivity.objects.update_or_create(
            username=self.username,
            defaults={'last_seen': now()}
        )

    @database_sync_to_async
    def get_last_seen(self, username):
        try:
            return UserActivity.objects.get(username=username).last_seen.strftime('%Y-%m-%d %H:%M:%S')
        except UserActivity.DoesNotExist:
            return "unknown"

    @database_sync_to_async
    def get_all_users(self):
        return list(User.objects.values_list('username', flat=True))
