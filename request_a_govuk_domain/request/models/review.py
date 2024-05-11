from django.db import models
from simple_history.models import HistoricalRecords
from .application import Application

NOTES_MAX_LENGTH = 500


# We've added simple-history to the dependencies but need to implement it,
# principally for this this class.
class Review(models.Model):
    """
    An extension of the Application class (has a one-to-one) relationship
    to hold details of the review carried out by the reviewing team. Each
    pair of Boolean/TextField fields represents something the reviewing
    team have to check or confirm before making a decision on the application.
    """

    application = models.OneToOneField(Application, on_delete=models.CASCADE)

    registrant_org_exists = models.BooleanField(default=False)
    registrant_org_exists_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    registrant_org_eligible = models.BooleanField(default=False)
    registrant_org_eligible_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    registrant_person_id_confirmed = models.BooleanField(default=False)
    registrant_person_id_confirmed_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    permission_signatory_role_confirmed = models.BooleanField(default=False)
    permission_signatory_role_confirmed_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    domain_name_validated = models.BooleanField(default=False)
    domain_name_validated_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    gds_exemption_validated = models.BooleanField(null=True)
    gds_exemption_validated_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    ministerial_request_validated = models.BooleanField(null=True)
    ministerial_request_validated_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    nac_appeal_validated = models.BooleanField(null=True)
    nac_appeal_validated_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    history = HistoricalRecords()

    def is_approvable(self) -> bool:
        if self.nac_appeal_validated:
            return True
        if all(
            (
                self.registrant_org_exists,
                self.registrant_org_eligible,
                self.registrant_person_id_confirmed,
                self.domain_name_validated,
            )
        ):
            return True
        return False

    def is_rejectable(self):
        # This logic needs some thought. That isn't to suggest the
        # logic above doesn't
        if self.nac_appeal_validated:
            return False
        return True

    def __str__(self):
        return str(self.application)

    class Meta:
        default_related_name = "review"


class ReviewFormGuidance(models.Model):
    name = models.CharField()
    how_to = models.CharField()
