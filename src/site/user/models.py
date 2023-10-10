from django.db import models
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    
    document = models.CharField(max_length=14, primary_key=True)
    nome_fantasia = models.CharField(max_length=100)
    razao_social = models.CharField(max_length=100)

    def __str__(self):
        name = f'{self.document} - {self.razao_social}'
        return name


class UserClient(AbstractUser):
    
    user_document = models.ManyToManyField(Client)
    
    whatsapp_number = models.CharField(max_length=20, unique=True, blank=True)
    whatsapp_chat_id = models.CharField(max_length=20, unique=True, blank=True)
    
    telegram_username = models.CharField(max_length=40, unique=True, blank=True)
    telegram_chat_id = models.CharField(max_length=20, unique=True, blank=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return str(self.user_document)