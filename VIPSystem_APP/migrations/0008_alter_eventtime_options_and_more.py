# Generated by Django 5.1.1 on 2024-12-17 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("VIPSystem_APP", "0007_eventticket"),
    ]

    operations = [
        migrations.AlterModelOptions(name="eventtime", options={"ordering": ["id"]},),
        migrations.AlterModelOptions(
            name="projectparticipation", options={"ordering": ["id"]},
        ),
        migrations.AlterModelOptions(
            name="staffprofile", options={"ordering": ["id"]},
        ),
        migrations.AlterModelOptions(name="vip", options={"ordering": ["id"]},),
    ]