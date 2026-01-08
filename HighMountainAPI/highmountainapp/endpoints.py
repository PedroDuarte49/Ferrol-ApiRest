import secrets

import bcrypt
from django.http import JsonResponse
import json

from HighMountainAPI.highmountainapp.models import CustomUser, UserSession, Foro, Comment


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

def post_foro(request,foro_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)
    token = request.headers.get('Authorization')

    if not token:
        return JsonResponse({'error': 'Token inválido'}, status=401)

    try:
        session = UserSession.objects.get(token=token)
    except UserSession.DoesNotExist:
        return JsonResponse({'error': 'Token inválido'}, status=401)

    try:
        body_json = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Comentario vacío'}, status=400)

    comment = body_json.get('comment')

    if not comment:
        return JsonResponse({'error': 'Comentario vacío'}, status=400)

    try:
        foro = Foro.objects.get(id=foro_id)
    except Foro.DoesNotExist:
        return JsonResponse({'error': 'Comentario vacío'}, status=400)

    # 4. Crear comentario
    Comment.objects.create(
        message=comment,
        user=session.user,
        foro=foro
    )

    return JsonResponse({'message': 'Comentario añadido'}, status=201)