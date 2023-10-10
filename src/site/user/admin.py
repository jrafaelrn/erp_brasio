from django.contrib import admin
from .models import Client, UserClient

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('document', 'nome_fantasia', 'razao_social')
    list_editable = ('nome_fantasia', 'razao_social')
    search_fields = ('document', 'nome_fantasia', 'razao_social')


@admin.register(UserClient)
class UserClientAdmin(admin.ModelAdmin):
    list_display = ('username', 'whatsapp_number', 'telegram_username')
    list_editable = ('whatsapp_number', 'telegram_username')
    search_fields = ('username', 'user_document', 'whatsapp_number', 'telegram_username')