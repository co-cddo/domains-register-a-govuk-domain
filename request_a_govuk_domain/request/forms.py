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
    Example form, please modify/ remove this when the actual requirements are 
    clear. This is only created to test the ui with gov uk design is working
    """
    registrant_full_name = forms.CharField(
        label='Registrant Full Name',
        max_length=100,
        widget=forms.TextInput(attrs={"class": "govuk-input"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                Fieldset(
                    Field.text(
                        "registrant_full_name",
                        field_width=Fluid.TWO_THIRDS),
                    ),
                Button("submit", "Save"),
            )
        if args and 'registrant_full_name' in args[0]:
            self.helper.layout.fields.append(Button.secondary(
                "cancel", "Back to Answers")
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
                Field.text("registrant_email_address",
                           field_width=Fluid.TWO_THIRDS),
            ),
            Button("submit", "Continue"),
        )
        if args and 'registrant_email_address' in args[0]:
            self.helper.layout.fields.append(Button.secondary(
                "cancel", "Back to Answers")
                )

class RegistrantTypeForm(forms.Form):
    REGISTRANT_TYPES = (
        Choice("central_gov",
               "Central government department or agency"),
        Choice("alb",
               "Non-departmental body - also known as an arm's length body"),
        Choice("fire_service",
               "Fire service"),
        Choice("county_council",
               "County, borough, metropolitan or district council"),
        Choice("parish_council",
               "Parish, town or community council"),
        Choice("village_council",
               "Neighbourhood or village council"),
        Choice("combined_authority",
               "Combined or unitary authority"),
        Choice("pcc",
               "Police and crime commissioner"),
        Choice("joint_authority",
               "Joint authority"),
        Choice("joint_committee",
               "Joint committee"),
        Choice("representing_public_sector",
               "Representing public sector bodies",
               divider="Or"),
        Choice("none",
               "None of the above"),
    )

    registrant_type = forms.ChoiceField(
        choices=REGISTRANT_TYPES,
        widget=forms.RadioSelect,
        label="Your registrant must be from an eligible organisation to get a .gov.uk domain name.",
        error_messages={
            "required": "Please select from one of the choices"
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios("registrant_type", legend_size=Size.SMALL),
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
        label="Does your registrant have an exemption from using the GOV.UK \
            website?",
        help_text="If your registrant is a central government department or \
            agency, they must have an exemption from the Government Digital \
            Service before applying for a new third-level .gov.uk domain \
            name.",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=forms.RadioSelect,
        error_messages={"required": "Are you exempted?"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "exe_radio", legend_size=Size.MEDIUM, legend_tag="h1", inline=True
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
            Button("submit", "Submit"),
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
