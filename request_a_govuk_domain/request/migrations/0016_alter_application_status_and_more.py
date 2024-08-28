# Generated by Django 4.2.13 on 2024-08-20 09:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("request", "0015_historicalregistrar_historicalregistrant_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("in_progress", "In Progress"),
                    ("ready_2i", "Ready for 2i"),
                    ("more_information", "More Information"),
                    ("with_nac", "Currently with NAC"),
                    ("new", "New"),
                    ("duplicate_application", "Duplicate application"),
                    ("archive", "archive"),
                    ("failed_confirmation_email", "Failed Confirmation Email"),
                    ("failed_decision_email", "Failed Decision Email"),
                ],
                default="new",
                max_length=25,
            ),
        ),
        migrations.AlterField(
            model_name="historicalapplication",
            name="status",
            field=models.CharField(
                choices=[
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("in_progress", "In Progress"),
                    ("ready_2i", "Ready for 2i"),
                    ("more_information", "More Information"),
                    ("with_nac", "Currently with NAC"),
                    ("new", "New"),
                    ("duplicate_application", "Duplicate application"),
                    ("archive", "archive"),
                    ("failed_confirmation_email", "Failed Confirmation Email"),
                    ("failed_decision_email", "Failed Decision Email"),
                ],
                default="new",
                max_length=25,
            ),
        ),
    ]