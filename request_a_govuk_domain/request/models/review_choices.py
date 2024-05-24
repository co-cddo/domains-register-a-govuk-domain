from django.db import models
from django.utils.translation import gettext_lazy as _


class RegistrarDetailsReviewChoices(models.TextChoices):
    APPROVE = "approve", _(
        "Registrar's email address matches Registrar's recognised domain - approve"
    )
    REJECT = "reject", _(
        "Registrar's email address does not match Registrar's recognised domain - reject"
    )


class DomainNameAvailabilityReviewChoices(models.TextChoices):
    APPROVE = "approve", _(
        "Name is available and organisation has no existing third-level .gov.uk domain - approve"
    )
    HOLDING = "holding", _("Name not available - on hold awaiting response")
    REJECT = "reject", _("Name not available - reject")


class RegistrantOrgReviewChoices(models.TextChoices):
    APPROVE = "approve", _("Strong evidence exists - approve")
    HOLDING = "holding", _("Need more info - on hold, awaiting response")
    REJECT = "reject", _("Insufficient evidence exists - reject")


class RegistrantPersonReviewChoices(models.TextChoices):
    APPROVE = "approve", _("Strong evidence exists - approve")
    HOLDING = "holding", _("Need more info - on hold, awaiting response")
    REJECT = "reject", _("Insufficient evidence exists - reject")


class RegistrantPermissionReviewChoices(models.TextChoices):
    APPROVE = "approve", _("Strong evidence exists - approve")
    HOLDING = "holding", _("Need more info - on hold, awaiting response")
    REJECT = "reject", _("Insufficient evidence exists - reject")


class PolicyExemptionReviewChoices(models.TextChoices):
    APPROVE = "approve", _("Strong evidence exists - approve")
    HOLDING = "holding", _("Need more info - on hold, awaiting response")
    REJECT = "reject", _("Insufficient evidence exists - reject")


class DomainNameRulesReviewChoices(models.TextChoices):
    APPROVE = "approve", _("Meets domain naming rules - approve")
    HOLDING = "holding", _(
        "Organisation already has a third-level .gov.uk domain - on hold awaiting response"
    )
    REJECT_NAME = "reject", _(
        "Does not meet naming rules - reject unless minister/perm sec request"
    )


class RegistrantSeniorSupportReviewChoices(models.TextChoices):
    APPROVE = "approve", _("Strong evidence exists - approve")
    HOLDING = "holding", _("Need more info - on hold, awaiting response")
    REJECT = "reject", _("Insufficient evidence exists - reject")


class RegistryDetailsReviewChoices(models.TextChoices):
    APPROVE = "approve", _("Role and/or email address meet guidelines - approved")
    HOLDING = "holding", _("Need more info - on hold/awaiting response")
    REJECT = "reject", _("Role and/or email address does not meet guidelines - reject")
