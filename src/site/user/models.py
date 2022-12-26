from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    document = models.CharField(max_length=14, primary_key=True)
    nome_fantasia = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=100)

    def __str__(self):
        return self.razao_social


class UserClient(models.Model):
    user_document = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user_document