from django import forms
from django.core.validators import EmailValidator
from django.template.defaultfilters import filesizeformat
from django.conf import settings

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
