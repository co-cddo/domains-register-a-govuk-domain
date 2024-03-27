from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Person(models.Model):
    name = models.CharField()  # We don't need to set a max under Django 4.2
    email_address = models.EmailField(max_length=320)
    role = models.CharField(null=True)
    phone_number = PhoneNumberField(blank=True)

    def __str__(self):
        return self.name
