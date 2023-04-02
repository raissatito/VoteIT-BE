from django.urls import path
from .views import *

urlpatterns = [
    path('create-room', create_room, name='create_vote_room'),
    path('create-option', create_option, name='create_vote_option'),
    path('get-all-rooms', get_all_rooms, name='get_all_vote_rooms'),
    path('get-room/<str:id>', get_room, name='get_vote_room'),
    path('get-vote-option/<str:id>', get_vote_option, name='get_vote_option'),
    path('vote', vote, name='vote'),
    path('end-vote', end_vote, name='end_vote'),
]