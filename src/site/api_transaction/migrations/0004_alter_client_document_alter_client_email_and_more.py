# Generated by Django 4.1.5 on 2023-01-11 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_transaction', '0003_alter_transaction_closed_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='document',
            field=models.CharField(max_length=14, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='group',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone_number',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]