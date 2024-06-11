from django.db import models
from simple_history.models import HistoricalRecords
from .application import Application
from request_a_govuk_domain.request.models import review_choices

NOTES_MAX_LENGTH = 5000


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

    registrar_details = models.CharField(
        choices=review_choices.RegistrarDetailsReviewChoices.choices,
        blank=True,
        null=True,
    )
    registrar_details_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    domain_name_availability = models.CharField(
        choices=review_choices.DomainNameAvailabilityReviewChoices.choices,
        blank=True,
        null=True,
    )
    domain_name_availability_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    registrant_org = models.CharField(
        choices=review_choices.RegistrantOrgReviewChoices.choices, blank=True, null=True
    )
    registrant_org_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    registrant_person = models.CharField(
        choices=review_choices.RegistrantPersonReviewChoices.choices,
        blank=True,
        null=True,
    )
    registrant_person_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    registrant_permission = models.CharField(
        choices=review_choices.RegistrantPermissionReviewChoices.choices,
        blank=True,
        null=True,
    )
    registrant_permission_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    policy_exemption = models.CharField(
        choices=review_choices.PolicyExemptionReviewChoices.choices,
        blank=True,
        null=True,
    )
    policy_exemption_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    domain_name_rules = models.CharField(
        choices=review_choices.DomainNameRulesReviewChoices.choices,
        blank=True,
        null=True,
    )
    domain_name_rules_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    registrant_senior_support = models.CharField(
        choices=review_choices.RegistrantSeniorSupportReviewChoices.choices,
        blank=True,
        null=True,
    )
    registrant_senior_support_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    registry_details = models.CharField(
        choices=review_choices.RegistryDetailsReviewChoices.choices,
        blank=True,
        null=True,
    )
    registry_details_notes = models.TextField(
        max_length=NOTES_MAX_LENGTH, blank=True, null=True
    )

    reason = models.TextField(max_length=NOTES_MAX_LENGTH, blank=True, null=True)

    history = HistoricalRecords()

    def is_approvable(self) -> bool:
        return True

    def is_rejectable(self):
        return True

    def __str__(self):
        return str(self.application)

    class Meta:
        default_related_name = "review"


class ReviewFormGuidance(models.Model):
    name = models.CharField()
    how_to = models.CharField()
