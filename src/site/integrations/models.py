from django.db import models

# Create your models here.
class Integration(models.Model):
    client_document = models.CharField(max_length=14)
    integration_name = models.CharField(max_length=100)
    integration_api_key = models.CharField(max_length=100)

    def __str__(self):
        return self.integration_name