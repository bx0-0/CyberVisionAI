# Generated by Django 5.1 on 2024-08-30 02:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bug_name', models.CharField(max_length=200)),
                ('asset', models.CharField(max_length=150)),
                ('step_and_POC', models.TextField(max_length=500)),
                ('report_file', models.FileField(editable=False, upload_to='')),
                ('create_at', models.DateField(auto_now_add=True)),
                ('severity', models.CharField(choices=[('Low', 'Low'), ('High', 'High'), ('Medium', 'Medium'), ('critical', 'critical')], default='Low', max_length=150)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
