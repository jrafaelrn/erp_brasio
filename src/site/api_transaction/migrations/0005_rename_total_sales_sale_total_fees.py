# Generated by Django 4.1.5 on 2023-01-11 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_transaction', '0004_alter_client_document_alter_client_email_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sale',
            old_name='total_sales',
            new_name='total_fees',
        ),
    ]
