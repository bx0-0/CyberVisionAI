# Generated by Django 5.1 on 2024-09-01 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('note', '0004_alter_notes_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='notes',
            name='Category',
            field=models.CharField(default='General', max_length=100),
        ),
    ]
