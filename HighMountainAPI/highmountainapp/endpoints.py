import secrets

import bcrypt
from django.http import JsonResponse
import json

from highmountainapp.models import CustomUser, UserSession


def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)
    body_json = json.loads(request.body)
    required_fields = ['user_email', 'user_password']
    if not all(field in body_json for field in required_fields):
        return JsonResponse({'error': 'Missing parameter'}, status=400)
    json_username = body_json['user_username']
    json_password = body_json['user_password']
    try:
        db_user = CustomUser.objects.get(email=json_username)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not in our system"}, status=404)

    if bcrypt.checkpw(json_password.encode('utf8'), db_user.encrypted_password.encode('utf8')):
        random_token = secrets.token_hex(10)
        session = UserSession(user=db_user, token=random_token)
        session.save()
        return JsonResponse({"token": random_token}, status=201)

    else:
        return JsonResponse({"error": "Invalid password"}, status=401)

def register_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)
    body_json = json.loads(request.body)
    required_fields = ['user_email', 'user_password']
    if not all(field in body_json for field in required_fields):
        return JsonResponse({'error': 'Missing parameter'}, status=400)
    json_username = body_json['user_username']
    json_password = body_json['user_password']
    try:
        CustomUser.objects.get(email=json_username)
        return JsonResponse({"error": "User already exists"}, status=409)
    except CustomUser.DoesNotExist:
        encrypted_password = bcrypt.hashpw(json_password.encode('utf8'), bcrypt.gensalt())
        new_user = CustomUser(username=json_username, encrypted_password=encrypted_password.decode('utf8'))
        new_user.save()
        return JsonResponse({"message": "User created successfully"}, status=200)