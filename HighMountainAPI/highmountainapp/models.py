from django.db import models

class CustomUser(models.Model):
    username = models.CharField(max_length=280, unique=True)
    encrypted_password = models.CharField(max_length=120)

class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(unique=True, max_length=30)

class Score(models.Model):
    player = models.CharField(max_length=15)
    points = models.IntegerField()

class Foro(models.Model):
    titulo = models.CharField(max_length=15)
    contenido = models.TextField()


class Comment(models.Model):
    message = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
