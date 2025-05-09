# Generated by Django 4.2.13 on 2024-06-12 11:49

from django.db import migrations, models

import request_a_govuk_domain.request.models.storage_util


class Migration(migrations.Migration):
    dependencies = [
        ("request", "0009_alter_application_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="ministerial_request_evidence",
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                storage=request_a_govuk_domain.request.models.storage_util.select_storage,
                upload_to="",
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="policy_exemption_evidence",
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                storage=request_a_govuk_domain.request.models.storage_util.select_storage,
                upload_to="",
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="written_permission_evidence",
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                storage=request_a_govuk_domain.request.models.storage_util.select_storage,
                upload_to="",
            ),
        ),
    ]
