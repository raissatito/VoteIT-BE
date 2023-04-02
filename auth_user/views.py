from .models import User
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from VoteIT.settings import SIMPLE_JWT
import json, datetime, jwt

@csrf_exempt
@api_view(['POST'])
def auth_login(request):
    deserialize = json.loads(request.body)
    username = deserialize["username"]
    password = deserialize["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        access = AccessToken.for_user(user)
        access.set_exp(lifetime=datetime.timedelta(days=30))
        return JsonResponse({'accessToken': str(access)}, status=status.HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Invalid'}, status=status.HTTP_401_UNAUTHORIZED)

@csrf_exempt
@api_view(['POST'])
def register(request):
    deserialize = json.loads(request.body)
    username = deserialize["username"]
    password = deserialize["password"]
    if not User.objects.filter(username=username).exists():
        print(username)
        print(password)
        user = User.objects.create_user(username=username, password=password)
        user.save()
        return JsonResponse({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse({'message': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@api_view(['GET'])
def get_username(request):
    user = is_authorized(request)
    if user is not None:
        return JsonResponse({'username': user.username}, status=status.HTTP_200_OK)
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