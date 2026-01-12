import secrets

import bcrypt
from django.http import JsonResponse
import json

from highmountainapp.models import CustomUser, UserSession
from highmountainapp.models import Score


def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'HTTP method unsupported'}, status=405)
    body_json = json.loads(request.body)
    json_username = body_json['user_username']
    json_password = body_json['user_password']
    try:
        db_user = CustomUser.objects.get(email=json_username)
    except CustomUser.DoesNotExist:
        pass

    if bcrypt.checkpw(json_password.encode('utf8'), db_user.encrypted_password.encode('utf8')):
        random_token = secrets.token_hex(10)
        session = UserSession(user=db_user, token=random_token)
        session.save()
        return JsonResponse({"token": random_token}, status=201)

    else:
        pass

    return JsonResponse({'message': 'User logged in successfully'})

def score_view(request):
    if request.method == 'GET':
        scores = Score.objects.all().order_by('-points')
        score_list = [{"player": s.player_name, "points": s.points} for s in scores]
        return JsonResponse({"scores": score_list}, status=200)

    elif request.method == 'POST':
        try:
            body_json = json.loads(request.body)
            player_name = body_json['player']
            points = body_json['points']
            if not player_name or not isinstance(points, int):
                return JsonResponse({"error": "Missing fields"}, status=400)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({"error": "Missing fields"}, status=400)
        score = Score(player_name=player_name, points=points)
        score.save()
        return JsonResponse({"message": "Score saved"}, status=201)

    else:
        return JsonResponse({"error": "HTTP method unsupported"}, status=405)