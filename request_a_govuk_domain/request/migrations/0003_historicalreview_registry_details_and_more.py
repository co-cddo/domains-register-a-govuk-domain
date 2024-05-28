# Generated by Django 4.2.13 on 2024-05-24 10:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("request", "0002_alter_application_written_permission_evidence"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalreview",
            name="registry_details",
            field=models.CharField(
                blank=True,
                choices=[
                    ("approve", "Role and/or email address meet guidelines - approved"),
                    ("holding", "Need more info - on hold/awaiting response"),
                    (
                        "reject",
                        "Role and/or email address does not meet guidelines - reject",
                    ),
                ],
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="historicalreview",
            name="registry_details_notes",
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="review",
            name="registry_details",
            field=models.CharField(
                blank=True,
                choices=[
                    ("approve", "Role and/or email address meet guidelines - approved"),
                    ("holding", "Need more info - on hold/awaiting response"),
                    (
                        "reject",
                        "Role and/or email address does not meet guidelines - reject",
                    ),
                ],
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="review",
            name="registry_details_notes",
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]