from django.db import models


class RegistrantTypeChoices(models.TextChoices):
    central_government = "Central government department or agency"
    ndpb = "Non-departmental body - also known as an arm's length body"
    parish_council = "Parish or community council"
    local_authority = "Town, county, borough, metropolitan or district council"
    fire_service = "Fire service"
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
    """
    An organisation seeking to register a new .gov.uk domain
    """

    name = models.CharField()
    type = models.CharField(choices=RegistrantTypeChoices.choices, max_length=100)

    def __str__(self):
        return self.name


class Registrar(models.Model):
    """
    An organisation which carries out the work to regsiter a new .gov.uk
    domain on behalf of a Registrant. The end-user flow is completed by
    an employee of the Registrar organisation in each case. Unlike
    Registrants, the list of possible Registrars is limited and approved
    in advance.
    """

    name = models.CharField(unique=True)

    def __str__(self):
        return self.name
