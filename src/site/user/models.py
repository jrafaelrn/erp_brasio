from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    document = models.CharField(max_length=14, primary_key=True)
    nome_fantasia = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=100)

    def __str__(self):
        return (f'{self.document} - {self.razao_social}')


class UserClient(AbstractUser):
    
    user_document = models.ForeignKey(Client, on_delete=models.DO_NOTHING, default='1')
    
    whatsapp_number = models.CharField(max_length=20, unique=True)
    whatsapp_chat_id = models.CharField(max_length=20, unique=True)
    
    telegram_username = models.CharField(max_length=40, unique=True)
    telegram_chat_id = models.CharField(max_length=20, unique=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.user_document