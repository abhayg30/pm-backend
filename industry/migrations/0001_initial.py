# Generated by Django 4.2.5 on 2024-07-30 00:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=255)),
                ('skills_req', models.CharField(max_length=2000)),
                ('short_description', models.CharField(max_length=1000)),
                ('description', models.CharField(max_length=7000)),
                ('vacancies', models.IntegerField()),
                ('location', models.CharField(max_length=255)),
                ('other_req', models.CharField(max_length=2000)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('closes_at', models.DurationField()),
                ('is_active', models.IntegerField()),
                ('job_status', models.IntegerField(choices=[('0', 'Not Started'), ('1', 'In Progress'), ('2', 'Finished')], default='0')),
                ('job_posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
