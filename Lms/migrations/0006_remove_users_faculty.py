# Generated by Django 4.2.2 on 2023-08-24 06:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Lms', '0005_remove_users_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='faculty',
        ),
    ]