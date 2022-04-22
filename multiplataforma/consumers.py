from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class PackagesConsumer(WebsocketConsumer):

    def connect(self):
        
        self.room_name = "packages-update"
        self.room_group_name = "packages-update"
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
               'type': 'package_message',
               #'room' : 'solicitudes2',
               'message': text_data
            }
        )


    def package_message(self, event):
        
        message = event['message']
        # Send message to WebSocket
        self.send( message)