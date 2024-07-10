import logging
import re

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.translation import gettext_lazy as _

from .organisation import Registrant, Registrar
from .person import RegistryPublishedPerson, RegistrarPerson, RegistrantPerson
from .storage_util import select_storage, TEMP_STORAGE_ROOT
from ...settings import S3_STORAGE_ENABLED

REF_NUM_LENGTH = 17
logger = logging.getLogger(__name__)


class ApplicationStatus(models.TextChoices):
    # We're likely to have to add to this with (at least) an
    # "Appealed to NAC" status.
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    IN_PROGRESS = "in_progress", _("In Progress")
    READY_2I = "ready_2i", _("Ready for 2i")
    MORE_INFORMATION = "more_information", _("More Information")
    NEW = "new", _("New")
    FAILED_CONFIRMATION_EMAIL = "failed_confirmation_email", _(
        "Failed Confirmation Email"
    )
    FAILED_DECISION_EMAIL = "failed_decision_email", _("Failed Decision Email")


class Application(models.Model):
    """
    The core model for the service, to which all other models in some way
    relate. An Application instance is created at the conclusion of the
    end-user journey. Additional attributes are then added (via the Review
    class) by the reviewer team.
    """

    id = models.BigAutoField(primary_key=True)
    reference = models.CharField(max_length=REF_NUM_LENGTH, null=False, unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    time_submitted = models.DateTimeField(auto_now_add=True)
    time_decided = models.DateTimeField(null=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NEW,
        max_length=25,
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
        null=True,
        blank=True,
        storage=select_storage,
        max_length=255,
    )
    ministerial_request_evidence = models.FileField(
        null=True,
        blank=True,
        storage=select_storage,
        max_length=255,
    )
    policy_exemption_evidence = models.FileField(
        null=True,
        blank=True,
        storage=select_storage,
        max_length=255,
    )

    def __str__(self):
        return f"{self.reference} - {self.domain_name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """
        When the application is saved, move the temporary files to the applications directory
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        if S3_STORAGE_ENABLED:
            storage = select_storage()
            # Move any temporary files in to the application specific folder
            # We have to do this custom moving because we store the initially uploaded
            # files in the temp location.
            for file_field in [
                self.policy_exemption_evidence,
                self.ministerial_request_evidence,
                self.written_permission_evidence,
            ]:
                if file_field and not file_field.name.startswith("applications"):
                    from_path = TEMP_STORAGE_ROOT + file_field.name
                    if file_field.file and isinstance(
                        file_field.file, InMemoryUploadedFile
                    ):
                        """
                        Sometimes the file is stored in the memory instead of the S3 bucket (i.e when uploaded
                        directly through the admin screens). Then
                        we have to move it in to S3 explicitly before continue with the usual S3 copy
                        """
                        storage.connection.meta.client.put_object(
                            Bucket=storage.bucket_name,
                            Key=from_path,
                            Body=file_field.file.read(),
                        )

                    to_path = f"applications/{self.reference}/" + re.sub(
                        r"[^A-Za-z0-9.]+", "_", file_field.name
                    )
                    logger.info(
                        "Copying temporary file %s to application folder %s",
                        from_path,
                        to_path,
                    )
                    storage.connection.meta.client.copy_object(
                        Bucket=storage.bucket_name,
                        CopySource=storage.bucket_name + "/" + from_path,
                        Key=to_path,
                    )
                    storage.delete(from_path)
                    file_field.name = to_path
        super().save(force_insert, force_update, using, update_fields)
