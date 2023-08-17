# Generated by Django 4.2.2 on 2023-08-17 07:26

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Lms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='user_files/')),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('edited_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Lms.users')),
            ],
        ),
    ]
