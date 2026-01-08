import secrets

import bcrypt
from django.http import JsonResponse
import json

from highmountainapp.models import CustomUser, UserSession

from HighMountainAPI.highmountainapp.models import Foro


def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)
    body_json = json.loads(request.body)
    json_username = body_json['user_username']
    json_password = body_json['user_password']
    try:
        db_user = CustomUser.objects.get(email=json_username)
    except CustomUser.DoesNotExist:
        pass  # No existe el usuario. En la siguiente tarea lo gestionamos

    if bcrypt.checkpw(json_password.encode('utf8'), db_user.encrypted_password.encode('utf8')):
        random_token = secrets.token_hex(10)
        session = UserSession(user=db_user, token=random_token)
        session.save()
        return JsonResponse({"token": random_token}, status=201)

    else:
        pass  # Contraseña incorrecta. En la siguiente tarea lo gestionamos

    return JsonResponse({'message': 'User logged in successfully'})

def foros(request):
    if request.method == 'GET':
        foros = Foro.objects.all()
        data = []
        for foro in foros:
            data.append({
                "id": foro.id,
                "title": foro.title
            })
        return JsonResponse({}, status=200)
    else:
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)

