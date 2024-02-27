from django import forms
from django.template.defaultfilters import filesizeformat
from django.conf import settings

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Button,
    Field,
    Fieldset,
    Fluid,
    Layout,
    Size
)

from .base_form import FormWithLabelStyle


class NameForm(FormWithLabelStyle):
    """
    Example form, please modify/ remove this when the actual requirements are clear
    This is only created to test the ui with gov uk design is working
    """
    registrant_full_name = forms.CharField(label='Registrant Full Name', max_length=100,
                                           widget=forms.TextInput(attrs={"class": "govuk-input"}))


class EmailForm(forms.Form):
    """
    Another example form
    This is an example of Crispy forms with govuk design system
    https://github.com/wildfish/crispy-forms-gds
    """
    registrant_email_address = forms.CharField(
        label="Email",
        help_text="Enter your email address.",
        widget=forms.EmailInput,
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

    def clean_registrant_email_address(self):
        """
        Example custom validation for email address
        Checks that the email address ends with .gov.uk
        """
        registrant_email_address = self.cleaned_data.get('registrant_email_address')

        if not registrant_email_address.endswith('.gov.uk'):
            raise forms.ValidationError("Email address must end with .gov.uk")

        return registrant_email_address


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
            Field.radios("exe_radio",
                         legend_size=Size.MEDIUM,
                         legend_tag="h1",
                         inline=True),
            Button("submit", "Continue"),
        )

    def get_choice(self, field):
        value = self.cleaned_data[field]
        return dict(self.fields[field].choices).get(value)


class ExemptionUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload a file",
        help_text="Support file is .jpeg or .png and the maximum size is 2.5 MB.",
        error_messages={
            "required": "Choose the file you want to upload."
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                Field.text("file", field_width=Fluid.TWO_THIRDS),
            ),
            Button("submit", "Submit"))

    def clean_file(self):
        """
        Custom Error messages for
        1. Size
        2. Content Type
        """
        file = self.cleaned_data.get('file')
        file_content = file.content_type.split('/')[0]

        if file_content in settings.CONTENT_TYPES:
            if file.size > int(settings.MAX_UPLOAD_SIZE):
                raise forms.ValidationError(('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(file.size)))
        else:
            raise forms.ValidationError('Support file is .jpeg or .png and the maximum size is 2.5 MB.')

        return file
