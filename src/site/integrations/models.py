from django.db import models
from user.models import Client

# Create your models here.
class Integration(models.Model):
    
    client_document = models.ForeignKey(Client, on_delete=models.DO_NOTHING)
    integration_name = models.CharField(max_length=100)
    integration_client_id = models.CharField(max_length=100)
    integration_api_key = models.CharField(max_length=100)

    def __str__(self):
        return self.integration_name