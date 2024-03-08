from django.db import models
from simple_history.models import HistoricalRecords

NOTES_MAX_LENGTH = 500


class Review(models.Model):
    registrant_org_exists = models.BooleanField(default=False)
    registrant_org_exists_notes = models.TextField(max_length=NOTES_MAX_LENGTH)

    registrant_org_eligible = models.BooleanField(default=False)
    registrant_org_eligible_notes = models.TextField(max_length=NOTES_MAX_LENGTH)

    registrant_person_id_confirmed = models.BooleanField(default=False)
    registrant_person_id_confirmed_notes = models.TextField(max_length=NOTES_MAX_LENGTH)

    permission_signatory_role_confirmed = models.BooleanField(default=False)
    permission_signatory_role_confirmed_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH
    )

    domain_name_validated = models.BooleanField(default=False)
    domain_name_validated_notes = models.TextField(max_length=NOTES_MAX_LENGTH)

    gds_exemption_validated = models.BooleanField(null=True)
    gds_exemption_validated_notes = models.TextField(max_length=NOTES_MAX_LENGTH)

    ministerial_request_validated = models.BooleanField(null=True)
    ministerial_request_validated_notes = models.TextField(max_length=NOTES_MAX_LENGTH)

    nac_appeal_validated = models.BooleanField(null=True)
    nac_appeal_validated_notes = models.TextField(max_length=NOTES_MAX_LENGTH)

    history = HistoricalRecords()
