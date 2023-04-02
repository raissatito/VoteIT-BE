from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VotingRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room"]
        self.room_group_name = "vote_%s" % self.room_id
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
        # Handle incoming messages from clients
        pass

    async def send_vote_count(self, event):
        # Send vote count to clients in the group
        vote_list = event["votes"]
        await self.send(text_data=json.dumps(vote_list))

class RoomListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "room_list"
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
        # Handle incoming messages from clients
        pass

    async def send_room_list(self, event):
        # Send vote count to clients in the group
        room_list = event["room_list"]
        await self.send(text_data=json.dumps(room_list))
    
