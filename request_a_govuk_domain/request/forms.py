from django import forms
from django.core.validators import EmailValidator
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from crispy_forms_gds.choices import Choice

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Button,
    Field,
    Fieldset,
    Fluid,
    HTML,
    Layout,
    Size,
)

from .utils import organisations_list


class NameForm(forms.Form):
    """
    Example form
    This is an example of Crispy forms with govuk design system
    https://github.com/wildfish/crispy-forms-gds
    """

    registrant_full_name = forms.CharField(
        label="Registrant Full Name",
        help_text="Enter your name as it appears on your passport.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                Field.text("registrant_full_name"),
            ),
            Button("submit", "Continue"),
        )


class EmailForm(forms.Form):
    registrant_email_address = forms.CharField(
        label="Email address of the .gov.uk Approved Registrar",
        widget=forms.EmailInput,
        validators=[EmailValidator("Please enter a valid email address")],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                Field.text("registrant_email_address", field_width=Fluid.TWO_THIRDS),
            ),
            Button("submit", "Continue"),
        )


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


class ConfirmForm(forms.Form):
    pass


class ExemptionForm(forms.Form):
    exe_radio = forms.ChoiceField(
        label="",
        help_text="If your registrant is a central government department or \
            agency, they must have an exemption from the Government Digital \
            Service before applying for a new third-level .gov.uk domain \
            name.",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=forms.RadioSelect,
        error_messages={"required": "Please answer Yes or No"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "exe_radio",
                legend_size=Size.MEDIUM,
                legend_tag="h1",
                inline=True,
            ),
            Button("submit", "Continue"),
        )

    def get_choice(self, field):
        value = self.cleaned_data[field]
        return dict(self.fields[field].choices).get(value)


class ExemptionUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload a file",
        help_text="Support file is .jpeg or .png and the maximum size is 2.5 MB.",
        error_messages={"required": "Choose the file you want to upload."},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                Field.text("file", field_width=Fluid.TWO_THIRDS),
            ),
            Button("submit", "Upload evidence"),
        )

    def clean_file(self):
        """
        Custom Error messages for
        1. Size
        2. Content Type
        """
        file = self.cleaned_data.get("file")
        if (
            file is not None
            and file.content_type.split("/")[0] in settings.CONTENT_TYPES
        ):
            if file.size > int(settings.MAX_UPLOAD_SIZE):
                raise forms.ValidationError(
                    ("Please keep filesize under %s. Current filesize %s")
                    % (
                        filesizeformat(settings.MAX_UPLOAD_SIZE),
                        filesizeformat(file.size),
                    )
                )
        else:
            raise forms.ValidationError(
                "Support file is .jpeg or .png and the maximum size is 2.5 MB."
            )

        return file


class RegistrarForm(forms.Form):
    """
    Registrar Form with organisations choice fields
    """

    organisations_choice = forms.ChoiceField(
        label="Choose your organisation",
        error_messages={"required": "Please select an item from the list"},
        choices=tuple(organisations_list()),
        widget=forms.Select(attrs={"class": "govuk-select"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                Field.text("organisations_choice"),
            ),
            HTML.warning(
                """If you are not listed as a .gov.uk Approved Registrar
                on the registry operator's website, you cannot use
                this service."""
            ),
            Button("submit", "Submit"),
        )


class DomainPurposeForm(forms.Form):
    DOMAIN_PURPOSES = (
        Choice("website_email", "Website and email address"),
        Choice("email-only", "Email address only", divider="or"),
        Choice("api", "API", hint="For example, hmrc01application.api.gov.uk"),
        Choice("service", "Service", hint="For example, get-a-fishing-licence.gov.uk"),
        Choice(
            "campaign",
            "Campaign",
            hint="For example, helpforhouseholds.campaign.gov.uk",
        ),
        Choice(
            "inquiry",
            "Independent inquiry",
            hint="For example, icai.independent.gov.uk",
        ),
        Choice("blog", "Blog", hint="For example, gds.blog.gov.uk"),
        Choice("dataset", "Dataset", hint="For example, coronavirus.data.gov.uk"),
    )

    domain_purpose = forms.ChoiceField(
        choices=DOMAIN_PURPOSES,
        widget=forms.RadioSelect,
        label="Tell us what you plan to use the .gov.uk domain name for. Select one option",
        error_messages={"required": "Please select from one of the choices"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios("domain_purpose", legend_size=Size.SMALL),
            Button("submit", "Continue"),
        )
