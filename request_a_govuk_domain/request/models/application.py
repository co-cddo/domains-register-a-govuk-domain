from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from .person import RegistryPublishedPerson, RegistrarPerson, RegistrantPerson
from .organisation import Registrant, Registrar
from .storage_util import select_storage

REF_NUM_LENGTH = 17


class ApplicationStatus(models.TextChoices):
    # We're likely to have to add to this with (at least) an
    # "Appealed to NAC" status.
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    IN_PROGRESS = "in_progress", _("In Progress")
    NEW = "new", _("New")


class Application(models.Model):
    """
    The core model for the service, to which all other models in some way
    relate. An Application instance is created at the conclusion of the
    end-user journey. Additional attributes are then added (via the Review
    class) by the reviewer team.
    """

    id = models.BigAutoField(primary_key=True)
    reference = models.CharField(max_length=REF_NUM_LENGTH, null=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    time_submitted = models.DateTimeField(auto_now_add=True)
    time_decided = models.DateTimeField(null=True)
    status = models.CharField(
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NEW,
        max_length=11,
    )
    # This is going to lead to duplicate persons and organisations. It's fine
    # for now pending working out what our intention is. We're not going to
    # enable users to select e.g. a registrant from a previous record so
    # perhaps we do nothing.
    domain_name = models.CharField(max_length=253)
    domain_purpose = models.CharField(null=True, blank=True)
    registrar_person = models.ForeignKey(
        RegistrarPerson, on_delete=models.CASCADE, related_name="registrar_application"
    )
    registrant_person = models.ForeignKey(
        RegistrantPerson,
        on_delete=models.CASCADE,
        related_name="registrant_application",
    )
    registry_published_person = models.ForeignKey(
        RegistryPublishedPerson,
        on_delete=models.CASCADE,
        related_name="registry_published_application",
    )
    registrant_org = models.ForeignKey(Registrant, on_delete=models.CASCADE)
    registrar_org = models.ForeignKey(Registrar, on_delete=models.CASCADE)
    written_permission_evidence = models.FileField(
        null=True, blank=True, storage=select_storage
    )
    ministerial_request_evidence = models.FileField(
        null=True, blank=True, storage=select_storage
    )
    policy_exemption_evidence = models.FileField(
        null=True, blank=True, storage=select_storage
    )

    def __str__(self):
        return f"{self.reference} - {self.domain_name}"
