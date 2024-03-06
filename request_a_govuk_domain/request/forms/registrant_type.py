from crispy_forms_gds.choices import Choice
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout, Field, Button
from crispy_forms_gds.layout.constants import Size
from django import forms


class RegistrantTypeForm(forms.Form):
    REGISTRANT_TYPES = (
        Choice("central_gov", "Central government department or agency"),
        Choice("alb", "Non-departmental body - also known as an arm's length body"),
        Choice("fire_service", "Fire service"),
        Choice("county_council", "County, borough, metropolitan or district council"),
        Choice("parish_council", "Parish, town or community council"),
        Choice("village_council", "Neighbourhood or village council"),
        Choice("combined_authority", "Combined or unitary authority"),
        Choice("pcc", "Police and crime commissioner"),
        Choice("joint_authority", "Joint authority"),
        Choice("joint_committee", "Joint committee"),
        Choice(
            "representing_public_sector",
            "Representing public sector bodies",
            divider="Or",
        ),
        Choice("none", "None of the above"),
    )

    registrant_type = forms.ChoiceField(
        choices=REGISTRANT_TYPES,
        widget=forms.RadioSelect,
        label="Your registrant must be from an eligible organisation to get a .gov.uk domain name.",
        error_messages={"required": "Please select from one of the choices"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios("registrant_type", legend_size=Size.SMALL),
            Button("submit", "Continue"),
        )
