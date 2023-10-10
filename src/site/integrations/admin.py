from django.contrib import admin
from .models import Integration, IntegrationTransaction


class IntegrationTransactionInline(admin.StackedInline):
    model = IntegrationTransaction

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    inlines = [IntegrationTransactionInline]
