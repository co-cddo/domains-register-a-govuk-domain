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

from .models.organisation import RegistrantTypeChoices, Registrar


def add_back_to_answers_button(args, field, layout):
    """
    Add the back button when coming to chnage the answer.
    """
    if args and field in args[0]:
        if args[0][field] != "":
            layout.fields.append(Button.secondary("cancel", "Back to Answers"))


class DomainForm(forms.Form):
    domain_name = forms.CharField(
        label="Domain name",
        help_text="Enter the .gov.uk domain name you want to get approval for",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                Field.text(
                    "domain_name"
                ),  # TODO: Crispy doesn't support text input suffixes so we might have to add it
            ),
            Button("submit", "Continue"),
        )
        add_back_to_answers_button(args, "domain_name", self.helper.layout)


class ApplicantDetailsForm(forms.Form):
    applicant_name = forms.CharField(
        label="Full name",
    )

    applicant_phone = forms.CharField(
        label="Telephone number",
        help_text="Your telephone number should be 11 digits. For example, 01632 660 001",
    )

    applicant_email = forms.CharField(
        label="Email address",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                HTML('<h2 class="govuk-heading-m">Applicant name</h2>'),
                Field.text("applicant_name", field_width=20),
            ),
            Fieldset(
                HTML('<h2 class="govuk-heading-m">Applicant contact details</h2>'),
                Field.text("applicant_phone", field_width=20),
                Field.text("applicant_email"),
            ),
            HTML(
                """<div class="govuk-inset-text">
            <span class="govuk-hint">An email to confirm your application will be sent to:</span><br>
            <p class="govuk-body govuk-!-font-size-24"></p></div>"""
            ),
            Button("submit", "Continue"),
        )
        add_back_to_answers_button(args, "applicant_name", self.helper.layout)


class RegistrantDetailsForm(forms.Form):
    registrant_full_name = forms.CharField(
        label="Full name",
    )

    registrant_phone = forms.CharField(
        label="Telephone number",
        help_text="Your telephone number should be 11 digits. For example, 01632 660 001",
    )

    registrant_email_address = forms.CharField(
        label="Email address",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                HTML('<h2 class="govuk-heading-m">Registrant name</h2>'),
                Field.text("registrant_full_name", field_width=20),
            ),
            Fieldset(
                HTML('<h2 class="govuk-heading-m">Registrant contact details</h2>'),
                Field.text("registrant_phone", field_width=20),
                Field.text("registrant_email_address"),
            ),
            HTML(
                """<div class="govuk-inset-text">An email to check identity will be sent to:</div>"""
            ),
            Button("submit", "Continue"),
        )
        add_back_to_answers_button(args, "registrant_full_name", self.helper.layout)


class RegistryDetailsForm(forms.Form):
    registrant_role = forms.CharField(
        label="Role name",
    )

    registrant_contact_phone = forms.CharField(
        label="Telephone number",
        help_text="Give a business telephone number and don't use personal",
    )

    registrant_contact_email = forms.CharField(
        label="Email address",
        help_text="Use a role-based email address, like support@romseyparishcouncil.gov.uk",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                HTML('<h2 class="govuk-heading-m">Registrant role</h2>'),
                Field.text("registrant_role", field_width=20),
            ),
            Fieldset(
                HTML('<h2 class="govuk-heading-m">Registrant contact details</h2>'),
                Field.text("registrant_contact_phone", field_width=20),
                Field.text("registrant_contact_email"),
            ),
            HTML(
                """<div class="govuk-warning-text">
                <span class="govuk-warning-text__icon" aria-hidden="true">!</span>
                <strong class="govuk-warning-text__text">
                <span class="govuk-visually-hidden">Warning</span>
                We will show all information collected on this page on the registry,
                which is open to the general public.
                </strong>
                </div>"""
            ),
            Button("submit", "Continue"),
        )
        add_back_to_answers_button(args, "registrant_role", self.helper.layout)


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
        add_back_to_answers_button(args, "registrant_email_address", self.helper.layout)


class RegistrantTypeForm(forms.Form):
    registrant_types = [
        Choice(*item) for item in RegistrantTypeChoices.__members__.items()
    ]
    registrant_types[-1].divider = "Or"
    registrant_types.append(Choice("none", "None of the above"))

    registrant_type = forms.ChoiceField(
        choices=registrant_types,
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


class RegistrantForm(forms.Form):
    registrant_organisation_name = forms.CharField(
        label="You must provide the formal legal name of your registrant’s organisation.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                Field.text("registrant_organisation_name"),
            ),
            HTML.warning(
                ": The Domains Team will reject applications if the registrant's organisation name does not match \
                official records or is spelled incorrectly."
            ),
            Button("submit", "Continue"),
        )
        add_back_to_answers_button(
            args, "registrant_organisation_name", self.helper.layout
        )


class WrittenPermissionForm(forms.Form):
    CHOICES = (
        Choice("Yes", "Yes"),
        Choice("No", "No"),
    )

    written_permission = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect,
        label="Your registrant must get written permission from a Chief Information Officer or equivalent you're \
        applying on behalf of a central government department or agency.",
        error_messages={"required": "Please answer Yes or No"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios("written_permission", legend_size=Size.SMALL, inline=True),
            Button("submit", "Continue"),
        )


class ExemptionForm(forms.Form):
    exe_radio = forms.ChoiceField(
        label="",
        help_text="If your registrant is a central government department or \
            agency, they must have an exemption from the Government Digital \
            Service before applying for a new third-level .gov.uk domain \
            name.",
        choices=(("Yes", "Yes"), ("No", "No")),
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
        add_back_to_answers_button(args, "exe_radio", self.helper.layout)

    def get_choice(self, field):
        value = self.cleaned_data[field]
        return dict(self.fields[field].choices).get(value)


class MinisterForm(forms.Form):
    minister_radios = forms.ChoiceField(
        label="",
        help_text="""If the requested .gov.uk domain does not meet the domain naming rules, it could still be approved if it has ministerial support. For example, the domain is needed to support the creation of a new government department or body.""",
        choices=(("Yes", "Yes"), ("No", "No")),
        widget=forms.RadioSelect,
        error_messages={"required": "Please answer Yes or No"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "minister_radios",
                legend_size=Size.MEDIUM,
                legend_tag="h1",
                inline=True,
            ),
            Button("submit", "Continue"),
        )
        add_back_to_answers_button(args, "minister_radios", self.helper.layout)

    def get_choice(self, field):
        value = self.cleaned_data[field]
        return dict(self.fields[field].choices).get(value)


class UploadForm(forms.Form):
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
            raise forms.ValidationError("Wrong file format. Please upload an image.")

        return file


class RegistrarForm(forms.Form):
    """
    Registrar Form with organisations choice fields
    """

    organisations_choice = forms.ChoiceField(
        label="Choose your organisation",
        choices=[],
        widget=forms.Select(attrs={"class": "govuk-select"}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        registrars = [("", "")] + list(
            (f"registrar-{registrar.id}", registrar.name)
            for registrar in Registrar.objects.all()
        )

        self.fields["organisations_choice"].choices = registrars

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
        add_back_to_answers_button(args, "organisations_choice", self.helper.layout)


class DomainPurposeForm(forms.Form):
    DOMAIN_PURPOSES = (
        Choice("website-email", "Website and email address"),
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
