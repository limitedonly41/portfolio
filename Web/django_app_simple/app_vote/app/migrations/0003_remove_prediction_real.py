# Generated by Django 4.2.1 on 2023-05-06 05:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_prediction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prediction',
            name='real',
        ),
    ]
