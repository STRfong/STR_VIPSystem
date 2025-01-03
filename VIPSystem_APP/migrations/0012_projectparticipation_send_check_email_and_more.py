# Generated by Django 5.1.1 on 2024-12-25 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("VIPSystem_APP", "0011_projectparticipation_notes"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectparticipation",
            name="send_check_email",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="projectparticipation",
            name="send_remind_email",
            field=models.BooleanField(default=False),
        ),
    ]
