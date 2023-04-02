from auth_user.models import User
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from VoteIT.settings import SIMPLE_JWT
from .models import VoteRoom, VoteOption
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json, datetime, jwt


@csrf_exempt
@api_view(['POST'])
def create_room(request):
    user = is_authorized(request)
    if user is not None:
        deserialize = json.loads(request.body)
        room_id = deserialize['room_id']
        name = deserialize['name']
        is_private = deserialize['is_private']
        print(room_id, name, is_private)
        room = VoteRoom(room_id=room_id, name=name, creator=user, is_private=is_private)
        room.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "room_list",
            {"type": "send_room_list", "room_list": VoteRoom.objects.filter(is_private=False, is_finished=False).order_by("-room_id").values()[::1]}
        )
        return JsonResponse({'message': 'Room Created'}, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'message': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)
    
@csrf_exempt
@api_view(['POST'])
def create_option(request):
    deserialize = json.loads(request.body)
    room_id = deserialize['room_id']
    vote_option = deserialize['vote_option']
    for i in vote_option:
        option_model = VoteOption(room=VoteRoom.objects.get(room_id=room_id), vote_option=i)
        option_model.save()
    return JsonResponse({'message': 'Vote Option Created'}, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(['GET'])
def get_all_rooms(request):
    rooms = VoteRoom.objects.filter(is_private=False, is_finished=False).order_by("-room_id").values()[::1]
    return JsonResponse({"rooms": rooms}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET'])
def get_room(request, id):
    rooms = VoteRoom.objects.filter(room_id=id).values()[0]
    if len(rooms) != 0:
        return JsonResponse({"rooms": rooms}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({"message": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
    
@csrf_exempt
@api_view(['GET'])
def get_vote_option(request, id):
    votes = VoteOption.objects.filter(room=VoteRoom.objects.get(room_id=id)).order_by("id")
    serializer = VotesSerializer(votes, many=True)
    return JsonResponse({"votes": serializer.data}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
def vote(request):
    user = is_authorized(request)
    if user is not None:
        deserialize = json.loads(request.body)
        option_id = deserialize['id']
        previous_id = deserialize['previous_id']
        new_option = VoteOption.objects.get(id=option_id)

        if previous_id != 0:
            previous_option = VoteOption.objects.get(id=previous_id)
            previous_option.vote_amount -= 1
            previous_option.voter.remove(user)
            previous_option.save()
            
        else:
            room = new_option.room
            room.participant.add(user)
            room.save()

        new_option.vote_amount += 1
        new_option.voter.add(user)
        new_option.save()

        channel_layer = get_channel_layer()

        voteRoom = new_option.room
        votes = VoteOption.objects.filter(room=voteRoom).order_by("id")
        serializer = VotesSerializer(votes, many=True)
        async_to_sync(channel_layer.group_send)(
            'vote_%s' % new_option.room.room_id,
            {"type": "send_vote_count", "votes": serializer.data}
        )

        return JsonResponse({"message": "Vote Added"}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)
    
@csrf_exempt
@api_view(['POST'])
def end_vote(request):
    user = is_authorized(request)
    if user is not None:
        deserialize = json.loads(request.body)
        room_id = deserialize['room_id']
        room = VoteRoom.objects.get(room_id=room_id)

        if room.creator != user:
            return JsonResponse({"message": "You are not the creator"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            room.is_finished = True
            room.save()

            rooms = VoteRoom.objects.filter(room_id=room_id).values()[0]
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'vote_%s' % room_id,
                {"type": "send_room_ended", "rooms": rooms}
            )

            list_user = room.participant.all()
            async_to_sync(channel_layer.group_send)(
                "room_list",
                {"type": "send_room_list", "room_list": VoteRoom.objects.filter(is_private=False, is_finished=False).order_by("-room_id").values()[::1]}
            )
            for user in list_user:
                async_to_sync(channel_layer.group_send)(
                    'user_%s' % user.username,
                    {"type": "send_notification", "vote_room": rooms}
                )

            return JsonResponse({"message": "Vote Ended"}, status=status.HTTP_200_OK)

    else:
        return JsonResponse({'message': 'Authentication Failed'}, status=status.HTTP_401_UNAUTHORIZED)
    
def is_authorized(request):
    token = request.headers['Authorization']
    if token and token.split(' ')[0] == 'Bearer':
        token = token.split(' ')[1]
        try :
            payload = jwt.decode(token, SIMPLE_JWT['SIGNING_KEY'], "HS512")
            user = User.objects.get(username=payload['user_id'])
        except:
            return None
        return user
    else:
        return None
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class VotesSerializer(serializers.ModelSerializer):
    voter = UserSerializer(many=True)

    class Meta:
        model = VoteOption
        fields = ['id', 'room', 'vote_option', 'vote_amount', 'voter']

    def get_voter(self, obj):
        return [voter.username for voter in obj.voter.all()]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['voter'] = self.get_voter(instance)
        return data
