import secrets

import bcrypt
from django.http import JsonResponse
import json

from highmountainapp.models import CustomUser, UserSession


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

def get_foroId(request, id_foro):
    # Comprobar method
    if request.method != 'GET':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)

    # Leer token del header
    token = request.headers.get('Authorization')
    if not token:
        return JsonResponse({'error': 'Token inválido'}, status=401)

    # Comprobar si el token existe en BD
    try:
        UserSession.objects.get(token=token)
    except UserSession.DoesNotExist:
        return JsonResponse({'error': 'Token inválido'}, status=401)

    # Obtener foro
    try:
        foro = Foro.objects.get(id=id_foro)
    except Foro.DoesNotExist:
        return JsonResponse({'error': 'Foro no encontrado'}, status=404)

    # Obtener comentarios asociados
    comentarios = Comentario.objects.filter(foro=foro)

    # Construir respuesta
    data = {
        "desc": foro.descripcion,
        "comentarios": [
            {
                "username": c.usuario.username,
                "comentario": c.texto,
                "datetime": c.fecha.isoformat()
            }
            for c in comentarios
        ]
    }

    # Respuesta OK
    return JsonResponse(foros[id_foro], status=200)