from django.urls import re_path, path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import VotingRoomConsumer, RoomListConsumer

websocket_urlpatterns = [
    path('ws/vote/<str:room>/', VotingRoomConsumer.as_asgi()),
    path('ws/rooms/', RoomListConsumer.as_asgi()),
]