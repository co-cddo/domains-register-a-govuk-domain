from django.utils.translation import gettext_lazy as _
from django.db import models


class RegistrantTypeChoices(models.TextChoices):
    CENTRAL_GOVERNMENT = "central_government", _(
        "Central government department or agency"
    )
    ALB = "alb", _("Non-departmental body - also known as an arm's length body")
    PARISH_COUNCIL = "parish_council", _("Parish, small town or community council")
    LOCAL_AUTHORITY = "local_authority", _(
        "Town, county, borough, metropolitan or district council"
    )
    FIRE_SERVICE = "fire_service", _("Fire service")
    VILLAGE_COUNCIL = "village_council", _("Neighbourhood or village council")
    COMBINED_AUTHORITY = "combined_authority", _("Combined or unitary authority")
    PCC = "pcc", _("Police and crime commissioner")
    JOINT_AUTHORITY = "joint_authority", _("Joint authority")
    JOINT_COMMITTEE = "joint_committee", _("Joint committee")
    PSB_GROUP = "psb_group", _(
        "Organisation representing a group of public sector bodies"
    )
    PSB_PROFESSION = "psb_profession", _(
        "Organisation representing a profession across public sector bodies"
    )

    @classmethod
    def get_label(cls, code: str | None) -> str | None:
        """
        Get the translated label for a given code.

        E.g. if the code is "central_government" then this method will
        return "Central government department or agency"

        param: code (str): The code representing the Registrant Type.

        :return: str or None: The translated label corresponding to the code.
        """
        for choice in cls.choices:
            if choice[0] == code:
                return str(choice[1])
        return None


class Registrant(models.Model):
    """
    An organisation seeking to register a new .gov.uk domain
    """

    name = models.CharField()
    type = models.CharField(choices=RegistrantTypeChoices.choices, max_length=100)

    class Meta:
        unique_together = ("name", "type")

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
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
