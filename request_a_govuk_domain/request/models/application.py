from django.db import models
from .person import Person
from .organisation import Registrant, Registrar
from .review import Review

REF_NUM_LENGTH = 6


class ApplicationStatus(models.TextChoices):
    approved = "Approved"
    rejected = "Rejected"
    pending = "Pending"


class Application(models.Model):
    _reference = models.CharField(max_length=REF_NUM_LENGTH, blank=True)
    status = models.CharField(
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.pending,
        max_length=8,
    )
    domain_name = models.CharField(max_length=253)
    applicant = Person()
    registrant_person = Person()
    responsible_person = Person()
    registrant_org = Registrant()
    registrar = Registrar()
    written_permission_evidence = models.FileField
    review = Review()

    @property
    def reference(self):
        if not self._reference:
            self._reference = hex(self.id)[2:].upper().zfill(REF_NUM_LENGTH)
        return self._reference


class CentralGovernmentAttributes(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    domain_purpose = models.CharField()
    ministerial_request_evidence = models.FileField
    gds_exemption_evidence = models.FileField

    class Meta:
        default_related_name = "centralgovt"
