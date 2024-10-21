from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords


class Person(models.Model):
    """
    An abstract class with common fields required by concete classes which
    describe a person.
    """

    name = models.CharField()  # We don't need to set a max under Django 4.2
    email_address = models.EmailField(max_length=320)
    phone_number = PhoneNumberField(blank=True)

    # maintain history
    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class RegistrantPerson(Person):
    """
    Each application for permission to register a new .gov.uk domain must
    include details of a named person who represents the Registrant
    organisation for the purpose of the application.
    """

    pass

    class Meta:
        unique_together = ("name", "email_address", "phone_number")


class RegistrarPerson(Person):
    """
    Each application for permission to register a new .gov.uk domain must
    include details of a named person who represents the Registrar organisation.
    This will often be the person completing the end-user flow, but doesn't
    have to be.
    """

    registrar = models.ForeignKey("request.Registrar", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "email_address", "phone_number", "registrar")


class RegistryPublishedPerson(Person):
    """
    Registered domains must include details of a named person for inclusion in
    the registry. This will usually be an employee of the Registrant in a
    digital/technology administration role. It may be the RegistrantPerson for
    the purpose of the same application but doesn't have to be.
    """

    role = models.CharField()

    class Meta:
        unique_together = ("email_address", "role")
