from django.db import models


class RegistrationData(models.Model):
    """
    Example model, please modify/ remove this as appropriate during development
    """

    registrant_full_name = models.CharField(max_length=100)
    registrant_email_address = models.EmailField(max_length=100)
