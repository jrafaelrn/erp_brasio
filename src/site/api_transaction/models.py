from django.db import models
from integrations.models import IntegrationTransaction


class Client(models.Model):
    
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    document = models.CharField(max_length=14, null=True)
    group = models.CharField(max_length=100, blank=True)
    id = models.CharField(max_length=100, primary_key=True)
    


class Product(models.Model):
    
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=100, null=True)
    image_url = models.URLField(null=True)
    


class ProductSale(models.Model):
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    sale = models.ForeignKey('Sale', on_delete=models.PROTECT)
    quantity = models.FloatField(null=False, blank=False)
    unit = models.CharField(max_length=10, null=False, blank=False)
    
    unit_price = models.FloatField(null=False, blank=False)
    addition = models.FloatField(null=False, blank=False)
    
    # Price = Quantity * (unit_price + addition)
    price = models.FloatField(null=False, blank=False)
    
    options_price = models.FloatField(null=False, blank=False)
    
    # Total Price = price + options_price
    total_price = models.FloatField(null=False, blank=False)
    
    observations = models.CharField(max_length=100, null=True)
    
    
    
class Address(models.Model):
    
    street_name = models.CharField(max_length=100, null=True)
    street_number = models.CharField(max_length=10, null=True)
    neighborhood = models.CharField(max_length=100, null=True)
    complement = models.CharField(max_length=100, null=True)
    reference = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=10, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=50, null=True)
    latitude = models.CharField(max_length=15, null=True)
    longitude = models.CharField(max_length=15, null=True)
     
    

class Delivery(models.Model):
    
    # Mode = DEFAULT / EXPRESS / ECONOMIC / TAKE OUT
    mode = models.CharField(max_length=20, null=True)
    
    # Delivery_by = IFOOD / MERCHANT / CORREIOS
    delivery_by = models.CharField(max_length=20, null=True)
    
    delivery_date_time = models.DateTimeField(null=True)
    observations = models.CharField(max_length=100, null=True)    
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True)
    

    
class Payment(models.Model):
    
    value = models.FloatField(null=False, blank=False)
    currency = models.CharField(max_length=3, null=False, blank=False)
    
    # Type = ONLINE or OFFLINE
    type = models.CharField(max_length=20, null=False, blank=False)
    
    # Method = CASH / CREDIT / DEBIT / PIX
    method = models.CharField(max_length=20, null=False, blank=False)
    
    date = models.DateField()
    bank_account = models.CharField(max_length=20, null=True)
    
    details = models.CharField(max_length=100, null=True)
    


class Benefit(models.Model):
    
    value = models.FloatField(null=False, blank=False)
    
    # Target = CART / DELIVERY_FEE / ITEM / PROGRESSIVE
    target = models.CharField(max_length=20, null=False, blank=False)
    
    # SPONSORSHIP = IFOOD / MERCHANT / EXTERNAL
    sponsorship_name = models.CharField(max_length=20, null=False, blank=False)
    sponsorship_description = models.CharField(max_length=100, null=False, blank=False) 



class Fee(models.Model):
    
    # Type = SMALL_ORDER
    type = models.CharField(max_length=100, null=False)
    
    full_description = models.CharField(max_length=100, null=False)
    value = models.FloatField(null=False, blank=False)
    liabilities = models.CharField(max_length=200, null=False)
    

    
class Sale(models.Model):
    
    total_sales = models.FloatField(null=False, blank=False)
    total_discount = models.FloatField(null=False, blank=False)
    total_shipping = models.FloatField(null=False, blank=False)
    total_products = models.FloatField(null=False, blank=False)
    
    client = models.ForeignKey(Client, on_delete=models.PROTECT, null=True)
    delivery = models.ForeignKey(Delivery, on_delete=models.PROTECT, null=True)
    products = models.ManyToManyField(Product, through='ProductSale')
    payments = models.ManyToManyField(Payment)
    benefits = models.ManyToManyField(Benefit)
    fees = models.ManyToManyField(Fee)
    
    order_amount = models.FloatField(null=False, blank=False)
    prepaid_amount = models.FloatField(null=False, blank=False)
    pending_amount = models.FloatField(null=False, blank=False)
    




# Represents a sales transaction
class Transaction(models.Model):
    
    api_source = models.ForeignKey(IntegrationTransaction, on_delete=models.PROTECT)
    api_id = models.CharField(max_length=100, primary_key=True)
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField()
    
    models.UniqueConstraint(fields=['api', 'id_api'], name='unique_transaction')
    
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT)
    


    
##################################
#            IFOOD               #
##################################


class IfoodClient(models.Model):
    
    orders_count = models.IntegerField(null=True)
    segmentation = models.CharField(max_length=20, null=True)

class Ifood(models.Model):
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    display_id = models.CharField(max_length=10)
    order_type = models.CharField(max_length=20)
    order_timing = models.CharField(max_length=20)
    sales_channel = models.CharField(max_length=30)
    extra_info = models.CharField(max_length=100)
    
    ifood_client_details = models.ForeignKey(IfoodClient, on_delete=models.PROTECT, null=True)
    
    
    