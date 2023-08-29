# Generated by Django 4.2.4 on 2023-08-23 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=500)),
                ('role_type', models.CharField(choices=[('super_admin', 'Super Admin'), ('artist_manager', 'Artist Manager'), ('artist', 'Artist')], max_length=14)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('gender', models.CharField(blank=True, choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other')], max_length=1, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('dob', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'customuser',
            },
        ),
    ]