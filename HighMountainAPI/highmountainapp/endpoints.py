import secrets

import bcrypt
from django.http import JsonResponse
import json

from django.template.defaulttags import comment
from django.views.decorators.csrf import csrf_exempt
from .models import Foro, CustomUser, UserSession, Score, Comment


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

@csrf_exempt
def scoreboard(request):
    if request.method == 'GET':
        scores = Score.objects.all().order_by('-points')
        score_list = [{"player": s.player, "points": s.points} for s in scores]
        return JsonResponse({"scores": score_list}, status=200)

    elif request.method == 'POST':
        try:
            body_json = json.loads(request.body)
            player = body_json['player']
            points = body_json['points']
            if not player or not isinstance(points, int):
                return JsonResponse({"error": "Missing fields"}, status=400)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({"error": "Missing fields"}, status=400)
        score = Score(player=player, points=points)
        score.save()
        return JsonResponse({"message": "Score saved"}, status=201)

    else:
        return JsonResponse({"error": "HTTP method unsupported"}, status=405)
@csrf_exempt
def comentarios(request, id_foro):
    # Comprobar method
    if request.method == 'POST':
        # Leer token del header
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'error': 'Token requerido'}, status=401)

        # Validar token
        try:
            session = UserSession.objects.get(token=token)
            usuario = session.user
        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Token inválido'}, status=401)

        # Obtener foro
        try:
            foro = Foro.objects.get(id=id_foro)
        except Foro.DoesNotExist:
            return JsonResponse({'error': 'Foro no encontrado'}, status=404)

        # Leer body
        try:
            body_json = json.loads(request.body)
            texto = body_json.get('comentario')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        if not texto:
            return JsonResponse({'error': 'El comentario no puede estar vacío'}, status=400)

        # Crear comentario
        comentario = Comment.objects.create(
            foro=foro,
            user=usuario,
            message=texto
        )

        return JsonResponse({
            "message": "Comentario creado",
            "username": comentario.user.username,
            "comentario": comentario.message,
            "datetime": comentario.datetime,
        }, status=201)

    elif request.method == 'GET':
        try:
            foro = Foro.objects.get(id=id_foro)
        except Foro.DoesNotExist:
            return JsonResponse({'error': 'Foro no encontrado'}, status=404)

            # Obtener comentarios asociados
        comentarios = Comment.objects.filter(foro=foro).order_by('datetime')

        # Construir respuesta
        data =  {
            "foro": {
                "id": foro.id,
                "titulo": foro.titulo,
                "contenido": foro.contenido
            },
            "comentarios": [
                {
                    "username": c.user.username,
                    "comentario": c.message,
                    "datetime": c.datetime,
                }
                for c in comentarios
            ]
        }

        # Respuesta OK
        return JsonResponse(data, status=200)

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


@csrf_exempt
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


