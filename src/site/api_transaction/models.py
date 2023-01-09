from django.db import models
from integrations.models import IntegrationTransaction


# Represents a sales transaction
class Transaction(models.Model):
    
    api = models.ForeignKey(IntegrationTransaction, on_delete=models.PROTECT, related_name='api_source')
    id = models.CharField(max_length=100, primary_key=True)
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField()
    
    
##################################
#            IFOOD               #
##################################

class Ifood(models.Model):
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='transaction_ifood')
    display_id = models.CharField(max_length=10)
    order_type = models.CharField(max_length=20)
    order_timing = models.CharField(max_length=20)
    sales_channel = models.CharField(max_length=30)
    extra_info = models.CharField(max_length=100)
    
    