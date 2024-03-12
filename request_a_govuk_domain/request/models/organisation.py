from django.db import models


class Organisation(models.Model):
    name = models.CharField()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class RegistrantTypeChoices(models.TextChoices):
    central_government = "Central government department or agency"
    ndpb = "Non-departmental body - also known as an arm's length body"
    fire_service = "Fire Service"
    local_authority = "County, borough, metropolitan or district council"
    parish_council = "Parish, town or community council"
    village_council = "Neighbourhood or village council"
    combined_authority = "Combined or unitary authority"
    pcc = "Police and Crime Commissioner"
    joint_authority = "Joint Authority"
    joint_committee = "Joint Committee"
    representative = "Representing public sector bodies"


class Registrant(Organisation):
    type = models.CharField(choices=RegistrantTypeChoices.choices, max_length=100)


class Registrar(Organisation):
    email_address = models.EmailField(max_length=320)
