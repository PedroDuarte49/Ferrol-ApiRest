import secrets

import bcrypt
from django.http import JsonResponse
import json

from django.views.decorators.csrf import csrf_exempt
from .models import Foro,CustomUser, UserSession

from .models import CustomUser, UserSession

@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)
    body_json = json.loads(request.body)
    required_fields = ['username', 'password']
    if not all(field in body_json for field in required_fields):
        return JsonResponse({'error': 'Missing parameter'}, status=400)
    json_username = body_json['username']
    json_password = body_json['password']
    try:
        db_user = CustomUser.objects.get(username=json_username)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User not in our system"}, status=404)

    if bcrypt.checkpw(json_password.encode('utf8'), db_user.encrypted_password.encode('utf8')):
        random_token = secrets.token_hex(10)
        session = UserSession(user=db_user, token=random_token)
        session.save()
        return JsonResponse({"token": random_token}, status=201)

    else:
        return JsonResponse({"error": "Invalid password"}, status=401)

@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)
    body_json = json.loads(request.body)
    required_fields = ['username', 'password']
    if not all(field in body_json for field in required_fields):
        return JsonResponse({'error': 'Missing parameter'}, status=400)
    json_username = body_json['username']
    json_password = body_json['password']
    try:
        CustomUser.objects.get(username=json_username)
        return JsonResponse({"error": "User already exists"}, status=409)
    except CustomUser.DoesNotExist:
        encrypted_password = bcrypt.hashpw(json_password.encode('utf8'), bcrypt.gensalt())
        new_user = CustomUser(username=json_username, encrypted_password=encrypted_password.decode('utf8'))
        new_user.save()
        return JsonResponse({"message": "User created successfully"}, status=200)
    return JsonResponse({'message': 'User logged in successfully'})

def get_foroId(request, id_foro):
    # Comprobar method
    if request.method != 'GET':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)

    # Leer token del header TOKEN INNECESARIO SOLO USAMOS EL TOKEN PARA COMENTAR EN /FOROS/ID el resto no necesitan autenticacio nes una app abierta
    #token = request.headers.get('Authorization')
    #if not token:
        #return JsonResponse({'error': 'Token inválido'}, status=401)

    # Comprobar si el token existe en BD
    #try:
        #UserSession.objects.get(token=token)
    #except UserSession.DoesNotExist:
        #return JsonResponse({'error': 'Token inválido'}, status=401)

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


