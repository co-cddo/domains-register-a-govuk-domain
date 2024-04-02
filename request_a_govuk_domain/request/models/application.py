from django.db import models
from .person import RegistryPublishedPerson, RegistrarPerson, RegistrantPerson
from .organisation import Registrant, Registrar

REF_NUM_LENGTH = 17


class ApplicationStatus(models.TextChoices):
    # We're likely to have to add to this with (at least) an
    # "Appealed to NAC" status.
    approved = "Approved"
    rejected = "Rejected"
    pending = "Pending"


class Application(models.Model):
    """
    The core model for the service, to which all other models in some way
    relate. An Application instance is created at the conclusion of the
    end-user journey. Additional attributes are then added (via the Review
    class) by the reviewer team.
    """

    id = models.BigAutoField(primary_key=True)
    reference = models.CharField(max_length=REF_NUM_LENGTH, null=False)
    status = models.CharField(
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.pending,
        max_length=8,
    )
    # This is going to lead to duplicate persons and organisations. It's fine
    # for now pending working out what our intention is. We're not going to
    # enable users to select e.g. a registrant from a previous record so
    # perhaps we do nothing.
    domain_name = models.CharField(max_length=253)
    registrar_person = models.OneToOneField(
        RegistrarPerson, on_delete=models.CASCADE, related_name="registrar_application"
    )
    registrant_person = models.OneToOneField(
        RegistrantPerson,
        on_delete=models.CASCADE,
        related_name="registrant_application",
    )
    registry_published_person = models.OneToOneField(
        RegistryPublishedPerson,
        on_delete=models.CASCADE,
        related_name="registry_published_application",
    )
    registrant_org = models.OneToOneField(Registrant, on_delete=models.CASCADE)
    registrar_org = models.ForeignKey(Registrar, on_delete=models.CASCADE)
    written_permission_evidence = models.FileField()

    def __str__(self):
        return f"{self.reference} - {self.domain_name}"


class CentralGovernmentAttributes(models.Model):
    """
    An extension to the Application class (uses a one-to-one) relationship
    to avoid adding attributes which are relevant to only a small proportion
    of applications to all instances.
    """

    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    domain_purpose = models.CharField()
    ministerial_request_evidence = models.FileField(null=True, blank=True)
    gds_exemption_evidence = models.FileField(null=True, blank=True)

    def __str__(self):
        return str(self.application)

    class Meta:
        default_related_name = "centralgovt"
