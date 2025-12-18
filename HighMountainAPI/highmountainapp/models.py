from django.db import models

class CustomUser(models.Model):
    username = models.CharField(max_length=280, unique=True)
    encrypted_password = models.CharField(max_length=120)

class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(unique=True, max_length=30)


