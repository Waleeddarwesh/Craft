import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Notification

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        if self.user.is_authenticated and message:
            # Save the notification to the database
            Notification.objects.create(user=self.user, message=message)

            # Broadcast the message to the group
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    'type': 'send_notification',  # Updated event type
                    'message': message,
                }
            )

    def send_notification(self, event):  # Updated method name
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message,
    }))