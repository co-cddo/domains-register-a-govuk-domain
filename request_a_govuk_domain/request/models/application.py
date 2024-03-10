from django.db import models
from .person import Person
from .organisation import Registrant, Registrar

REF_NUM_LENGTH = 6


class ApplicationStatus(models.TextChoices):
    approved = "Approved"
    rejected = "Rejected"
    pending = "Pending"


class Application(models.Model):
    id = models.BigAutoField(primary_key=True)
    reference = models.CharField(max_length=REF_NUM_LENGTH, blank=True)
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
    applicant = models.OneToOneField(
        Person, on_delete=models.CASCADE, related_name="applicant_application"
    )
    registrant_person = models.OneToOneField(
        Person, on_delete=models.CASCADE, related_name="registrant_application"
    )
    responsible_person = models.OneToOneField(
        Person, on_delete=models.CASCADE, related_name="responsible_application"
    )
    registrant_org = models.OneToOneField(Registrant, on_delete=models.CASCADE)
    registrar = models.ForeignKey(Registrar, on_delete=models.CASCADE)
    written_permission_evidence = models.FileField(null=True, blank=True)

    # Pending research on the GOV.UK standard for creating reference numbers
    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            self.reference = hex(self.id)[2:].upper().zfill(REF_NUM_LENGTH)
        return super().save(*args, **kwargs)

    def __str__(self):
        reference = self.reference if self.reference else "No ref."
        return f"{reference} - {self.domain_name}"


class CentralGovernmentAttributes(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    domain_purpose = models.CharField()
    ministerial_request_evidence = models.FileField(null=True, blank=True)
    gds_exemption_evidence = models.FileField(null=True, blank=True)

    def __str__(self):
        return str(self.application)

    class Meta:
        default_related_name = "centralgovt"
