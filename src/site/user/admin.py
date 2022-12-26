from django.contrib import admin
from .models import Client, UserClient

admin.site.register(Client)
admin.site.register(UserClient)
