# Generated by Django 5.1.1 on 2024-09-20 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("VIPSystem_APP", "0002_alter_projectparticipation_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectparticipation",
            name="join_people_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="projectparticipation",
            name="token",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]