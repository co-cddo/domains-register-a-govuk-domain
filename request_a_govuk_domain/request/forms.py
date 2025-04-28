import re

from crispy_forms_gds.choices import Choice
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Button, Field, Fieldset, Fluid, Layout, Size
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.template.defaultfilters import filesizeformat

from ..layout.content import DomainsHTML
from .models.organisation import RegistrantTypeChoices, Registrar
from .utils import validate_file_infection
from .validators import PhoneNumberValidator


def domain_validator(domain_name: str):
    """Reject domain names which do not meet the RFCs:
    https://datatracker.ietf.org/doc/html/rfc1034#page-11,
    https://www.rfc-editor.org/rfc/rfc2181#section-11
    """
    domain_input_regexp = re.compile("^[a-z][a-z0-9-]+[a-z0-9](\\.gov\\.uk)?$")  # based on RFC1035

    if not (3 <= len(domain_name.split(".")[0]) <= 63):
        raise ValidationError("The .gov.uk domain name must be between 3 and 63 characters")
    if not domain_input_regexp.match(domain_name):
        raise ValidationError(
            "The .gov.uk domain name must only include a to z, alphanumberic characters and special characters such as hyphens."
        )


class RegistrarDetailsForm(forms.Form):
    """
    Registrar Form with organisations choice fields
    """

    registrar_organisation = forms.ChoiceField(
        label="Select your organisation from the list",
        choices=[],
        widget=forms.Select(attrs={"class": "govuk-select"}),
        required=True,
    )

    registrar_name = forms.CharField(
        label="Full name",
    )

    registrar_phone = forms.CharField(
        label="Telephone number",
        help_text="Enter a UK phone number",
        validators=[
            PhoneNumberValidator("Enter a telephone number, like 01632 960 001, 03034 443 000 or 07700 900 982")
        ],
    )

    registrar_email = forms.CharField(
        label="Email address",
        help_text="We will use this email to contact you about the application.",
        validators=[EmailValidator("Enter an email address in the correct format, like name@example.co.uk")],
    )

    def __init__(self, *args, **kwargs):
        self.change = kwargs.pop("change", None)
        super().__init__(*args, **kwargs)

        registrar_organisations = [("", "")] + list(
            (f"registrar-{registrar.id}", registrar.name) for registrar in Registrar.objects.filter(active=True)
        )

        self.fields["registrar_organisation"].choices = registrar_organisations

        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                DomainsHTML(
                    '<h2 class="govuk-heading-m" autocomplete="false">Organisation name</h2>'  # pragma: allowlist secret
                ),
                Field.text("registrar_organisation"),
            ),
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Contact details</h2>'),
                Field.text("registrar_name", field_width=20),
                Field.text("registrar_phone", field_width=20),
                Field.text("registrar_email"),
            ),
            Button("submit", "Continue"),
        )
        if self.change:
            self.helper.layout.fields.append(Button.secondary("back_to_answers", "Back to answers"))
        self.fields["registrar_organisation"].error_messages["required"] = "Select your organisation"
        self.fields["registrar_name"].error_messages["required"] = "Enter your full name"
        self.fields["registrar_phone"].error_messages["required"] = "Enter your telephone number"
        self.fields["registrar_email"].error_messages["required"] = "Enter your email address"


class RegistrantTypeForm(forms.Form):
    registrant_types = [Choice(*item) for item in RegistrantTypeChoices.choices]
    registrant_types[-1].divider = "Or"
    registrant_types.append(Choice("none", "None of the above"))

    registrant_type = forms.ChoiceField(
        choices=registrant_types,
        widget=forms.RadioSelect,
        label="Who is this domain name for?",
        help_text="Your registrant must be from an eligible organisation to get a .gov.uk domain name.",
        error_messages={"required": "Please select from one of the choices"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "registrant_type",
                legend_tag="h1",
                legend_size=Size.EXTRA_LARGE,
            ),
            Button("submit", "Continue"),
        )
        self.fields["registrant_type"].error_messages["required"] = "Select the registrant's organisation type"


class DomainForm(forms.Form):
    domain_name = forms.CharField(label="")

    def clean_domain_name(self) -> str:
        domain_typed: str = self.cleaned_data["domain_name"].strip().lower()
        if ".gov.uk" not in domain_typed:
            domain_typed = domain_typed + ".gov.uk"

        # check for the domain length and regex
        domain_validator(domain_typed)
        return domain_typed

    def __init__(self, *args, **kwargs):
        self.change = kwargs.pop("change", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                Field.text("domain_name"),
                DomainsHTML.warning(
                    "The Domains Team will check if this is available and decide whether to approve it."
                ),
            ),
            Button("submit", "Continue"),
        )
        if self.change:
            self.helper.layout.fields.append(Button.secondary("back_to_answers", "Back to answers"))
        self.fields["domain_name"].error_messages["required"] = "Enter the .gov.uk domain name you want to request"


class DomainConfirmationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.domain_name = kwargs.pop("domain_name", None)
        super().__init__(*args, **kwargs)
        self.fields["domain_confirmation"] = forms.ChoiceField(
            label=f"Is {self.domain_name} the correct domain name?",
            choices=(
                ("yes", "Yes, I confirm this is correct"),
                ("no", "No, I want to change it"),
            ),
            widget=forms.RadioSelect,
            help_text="The Domains Team will check if this is available and decide whether to approve it.",
            error_messages={"required": "Select yes if the requested .gov.uk domain name is correct"},
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "domain_confirmation",
                legend_size=Size.EXTRA_LARGE,
                legend_tag="h1",
                inline=False,
            ),
            Button("submit", "Continue"),
        )

    def get_choice(self, field):
        value = self.cleaned_data[field]
        return dict(self.fields[field].choices).get(value)

    class Meta:
        fields = ["domain_confirmation"]


class RegistrantDetailsForm(forms.Form):
    registrant_organisation = forms.CharField(
        label="Organisation name",
    )

    registrant_full_name = forms.CharField(
        label="Full name",
    )

    registrant_phone = forms.CharField(
        label="Telephone number",
        help_text="Enter a UK phone number",
        validators=[
            PhoneNumberValidator("Enter a telephone number, like 01632 960 001, 03034 443 000 or 07700 900 982")
        ],
    )

    registrant_email = forms.CharField(
        label="Email address",
        help_text="Use a current work email address for the registrant.",
        validators=[EmailValidator("Enter an email address in the correct format, like name@example.co.uk")],
    )

    def __init__(self, *args, **kwargs):
        self.change = kwargs.pop("change", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Organisation details</h2>'),
                DomainsHTML.p("You must provide the formal legal name of your registrant’s organisation."),
                DomainsHTML.p(
                    """The Domains Team will reject applications if the registrant’s
                organisation name does not match official records or is spelled incorrectly."""
                ),
                Field.text("registrant_organisation"),
            ),
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Contact details</h2>'),
                DomainsHTML.p("We are collecting the registrant’s personal contact details to confirm their identity."),
                Field.text("registrant_full_name", field_width=20),
                Field.text("registrant_phone", field_width=20),
                Field.text("registrant_email"),
            ),
            Button("submit", "Continue"),
        )
        if self.change:
            self.helper.layout.fields.append(Button.secondary("back_to_answers", "Back to answers"))
        self.fields["registrant_organisation"].error_messages["required"] = "Enter the registrant's organisation name"
        self.fields["registrant_full_name"].error_messages["required"] = "Enter the registrant's full name"
        self.fields["registrant_phone"].error_messages["required"] = "Enter the registrant's telephone number"
        self.fields["registrant_email"].error_messages["required"] = "Enter the registrant's current email address"


class RegistryDetailsForm(forms.Form):
    registrant_role = forms.CharField(
        label="Role name",
    )

    def __init__(self, *args, **kwargs):
        self.hint_email = kwargs.pop("hint_email", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.fields["registrant_contact_email"] = forms.CharField(
            label="Email address",
            help_text=f"Use a role-based email address, like {self.hint_email}.",
            validators=[
                EmailValidator(
                    """Enter the registrant's role-based email address in the correct format,
                    like itsupport@organisation.gov.uk"""
                )
            ],
        )
        self.helper.layout = Layout(
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Registrant role</h2>'),
                Field.text("registrant_role", field_width=20),
            ),
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Registrant contact details</h2>'),
                Field.text("registrant_contact_email"),
            ),
            Button("submit", "Continue"),
        )
        self.fields["registrant_role"].error_messages["required"] = "Enter the registrant's role name"
        self.fields["registrant_contact_email"].error_messages[
            "required"
        ] = "Enter the registrant's role-based email address"


class WrittenPermissionForm(forms.Form):
    CHOICES = (
        Choice("yes", "Yes"),
        Choice("no", "No"),
    )

    written_permission = forms.ChoiceField(
        label="Does your registrant have proof of permission to apply for a .gov.uk domain name?",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select yes if your registrant has permission to apply for a .gov.uk domain name"},
    )

    def __init__(self, *args, **kwargs):
        self.change = kwargs.pop("change", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios("written_permission", legend_size=Size.SMALL, inline=True),
            Button("submit", "Continue"),
        )


class ExemptionForm(forms.Form):
    exemption = forms.ChoiceField(
        label="Does your registrant have an exemption from using the GOV.UK website?",
        help_text="If your registrant is a central government department or \
            agency, they must have an exemption from the Government Digital \
            Service before applying for a new third-level .gov.uk domain \
            name.",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=forms.RadioSelect,
        error_messages={"required": "Select yes if your registrant has permission to apply for a .gov.uk domain name"},
    )

    def __init__(self, *args, **kwargs):
        self.change = kwargs.pop("change", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "exemption",
                legend_tag="h1",
                legend_size=Size.EXTRA_LARGE,
                inline=True,
            ),
            Button("submit", "Continue"),
        )

    def get_choice(self, field):
        value = self.cleaned_data[field]
        return dict(self.fields[field].choices).get(value)


class MinisterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.domain_name = kwargs.pop("domain_name", None)
        super().__init__(*args, **kwargs)
        self.fields["minister"] = forms.ChoiceField(
            label=f"Has a central government minister requested the {self.domain_name} domain name?",
            help_text="If the requested domain name does not meet the domain naming rules, it could still be approved if it has ministerial support.<br />For example, the domain is needed to support the creation of a new government department or body.",
            choices=(("yes", "Yes"), ("no", "No")),
            widget=forms.RadioSelect,
            error_messages={
                "required": "Select yes if a central government minister requested the .gov.uk domain name"
            },
        )
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "minister",
                legend_size=Size.EXTRA_LARGE,
                legend_tag="h1",
                inline=True,
            ),
            Button("submit", "Continue"),
        )

    def get_choice(self, field):
        value = self.cleaned_data[field]
        return dict(self.fields[field].choices).get(value)


class UploadForm(forms.Form):
    file = forms.FileField(
        label="Upload a file",
        help_text="We support JPEG, PNG or PDF files. The maximum upload size is %sMB."
        % filesizeformat(settings.MAX_UPLOAD_SIZE).split(".")[0],
        error_messages={"required": "Select the file you want to upload"},
        validators=[validate_file_infection],
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
        if file is not None and file.content_type.split("/")[1] in settings.CONTENT_TYPES:
            if file.size > int(settings.MAX_UPLOAD_SIZE):
                raise forms.ValidationError(("The selected file must be smaller than 10MB"))
        else:
            raise forms.ValidationError("The selected file must be a JPEG, PNG or PDF.")

        return file


class DomainPurposeForm(forms.Form):
    DOMAIN_PURPOSES = (
        Choice("website-email", "Website (may include email)"),
        Choice("email-only", "Email only domain", divider="or"),
        Choice("api", "API", hint="For example, hmrc01application.api.gov.uk"),
        Choice(
            "service",
            "Service",
            hint="For example, get-a-fishing-licence.service.gov.uk",
        ),
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
        label="Why do you want a .gov.uk domain name?",
        help_text="Tell us what you plan to use the .gov.uk domain name for.<br />Select one option",
        error_messages={"required": "Please select from one of the choices"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field.radios(
                "domain_purpose",
                legend_tag="h1",
                legend_size=Size.EXTRA_LARGE,
            ),
            Button("submit", "Continue"),
        )
        self.fields["domain_purpose"].error_messages[
            "required"
        ] = "Select what you plan to use the .gov.uk domain name for"


class ConfirmationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Button(
                "submit",
                "Accept and send",
            ),
        )
