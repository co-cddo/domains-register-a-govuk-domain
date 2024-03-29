from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Person(models.Model):
    name = models.CharField()  # We don't need to set a max under Django 4.2
    email_address = models.EmailField(max_length=320)
    phone_number = PhoneNumberField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class RegistrantPerson(Person):
    pass


class RegistrarPerson(Person):
    registrar = models.ForeignKey("request.Registrar", on_delete=models.CASCADE)


class RegistryPublishedPerson(Person):
    role = models.CharField()
