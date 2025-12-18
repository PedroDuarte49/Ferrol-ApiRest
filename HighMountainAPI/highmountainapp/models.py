from django.db import models

class CustomUser(models.Model):
    username = models.CharField(max_length=280, unique=True)
    encrypted_password = models.CharField(max_length=120)

class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(unique=True, max_length=30)

class Score(models.Model):
    id = models.AutoField(primary_key=True)
    player = models.CharField(max_length=15)
    points = models.IntegerField()

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    foro = models.ForeignKey(Score, on_delete=models.CASCADE)

class Foro(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=15)
    comments = models.ManyToManyField(Comment)
