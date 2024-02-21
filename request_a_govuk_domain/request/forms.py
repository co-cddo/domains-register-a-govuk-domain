from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Button,
    Field,
    Fieldset,
    Fluid,
    Layout,
    Size,
)
from django import forms

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
