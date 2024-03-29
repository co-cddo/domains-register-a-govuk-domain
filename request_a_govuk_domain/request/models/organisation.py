from django.db import models


class RegistrantTypeChoices(models.TextChoices):
    central_government = "Central government department or agency"
    ndpb = "Non-departmental body - also known as an arm's length body"
    parish_council = "Parish or community council"
    local_authority = "Town, county, borough, metropolitan or district council"
    fire_service = "Fire Service"
    village_council = "Neighbourhood or village council"
    combined_authority = "Combined or unitary authority"
    pcc = "Police and Crime Commissioner"
    joint_authority = "Joint Authority"
    joint_committee = "Joint Committee"
    representing_psb = "Organisation representing a group of public sector bodies"
    representing_profession = (
        "Organisation representing a profession across public sector bodies"
    )


class Registrant(models.Model):
    name = models.CharField()
    type = models.CharField(choices=RegistrantTypeChoices.choices, max_length=100)

    def __str__(self):
        return self.name


class Registrar(models.Model):
    name = models.CharField(unique=True)

    def __str__(self):
        return self.name
