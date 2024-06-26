# Generated by Django 4.2.13 on 2024-06-05 16:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("request", "0005_alter_historicalreview_registry_details_notes_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationResponseID",
            fields=[
                (
                    "id",
                    models.CharField(max_length=36, primary_key=True, serialize=False),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="application",
            name="reference",
            field=models.CharField(max_length=17, unique=True),
        ),
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("in_progress", "In Progress"),
                    ("new", "New"),
                    ("failed_confirmation_email", "Failed Confirmation Email"),
                    ("failed_decision_email", "Failed Decision Email"),
                ],
                default="new",
                max_length=25,
            ),
        ),
    ]
