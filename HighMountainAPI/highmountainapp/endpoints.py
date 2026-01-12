import secrets

import bcrypt
from django.http import JsonResponse
import json

from .models import Foro,CustomUser, UserSession


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
                "titulo": foro.titulo,
                "contenido": foro.contenido
            })
        return JsonResponse({"foros": data}, status=200)
    elif request.method == 'POST':
        # Crear un nuevo foro
        try:
            body_json = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        titulo = body_json.get('titulo')
        contenido = body_json.get('contenido')

        if not titulo or not contenido:
            return JsonResponse({'error': 'Se requiere título y contenido'}, status=400)

        nuevo_foro = Foro.objects.create(titulo=titulo, contenido=contenido)

        return JsonResponse({
            "id": nuevo_foro.id,
            "titulo": nuevo_foro.titulo,
            "contenido": nuevo_foro.contenido
        }, status=201)

    else:
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)


