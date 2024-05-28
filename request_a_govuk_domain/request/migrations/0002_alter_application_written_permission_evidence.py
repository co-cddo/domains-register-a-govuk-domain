# Generated by Django 4.2.13 on 2024-05-23 13:00

from django.db import migrations, models
import request_a_govuk_domain.request.models.storage_util


class Migration(migrations.Migration):
    dependencies = [
        ("request", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="written_permission_evidence",
            field=models.FileField(
                blank=True,
                null=True,
                storage=request_a_govuk_domain.request.models.storage_util.select_storage,
                upload_to="",
            ),
        ),
    ]