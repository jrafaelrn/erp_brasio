from django.db import models
from user.models import Client


class Integration(models.Model):
    
    client_document = models.ForeignKey(Client, on_delete=models.PROTECT)
    integration_name = models.CharField(max_length=100)
    status = models.CharField(max_length=30)
    
    models.UniqueConstraint(fields=['client_document', 'integration_name'], name='unique_integration')

    def __str__(self):
        return f'{self.client_document} - {self.integration_name}'
    
    def __eq__(self, other):
        return self.client_document == other.client_document and self.integration_name == other.integration_name
    
    def __hash__(self):
        return hash((self.client_document, self.integration_name))
    
    
class IntegrationTransaction(models.Model):
    
    integration = models.ForeignKey(Integration, on_delete=models.PROTECT, related_name='integration_transaction')
    identifier = models.CharField(max_length=100)    