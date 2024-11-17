from channels.generic.websocket import WebsocketConsumer
import json
from .models import EmailTracking

class EmailStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def receive(self, text_data):
        # Fetch latest email statuses from the database
        email_data = list(EmailTracking.objects.values('company_name', 'email_status', 'delivery_status', 'opened'))
        
        self.send(text_data=json.dumps({
            'email_statuses': email_data
        }))

    def disconnect(self, close_code):
        pass
