import re
from django import forms
from django.template.defaultfilters import filesizeformat
from django.conf import settings
from crispy_forms_gds.choices import Choice
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Button,
    Field,
    Fieldset,
    Fluid,
    Layout,
    Size,
)
from typing import Optional
from .models.organisation import RegistrantTypeChoices, Registrar
from ..layout.content import DomainsHTML
from .utils import validate_file_infection


class PhoneNumberValidator:
    phone_number_pattern = re.compile(r"^\s*\d(?:\s*\d){10}\s*$")

    def __init__(self, error_message=None):
        self.error_message = error_message or "Invalid phone number format"

    def __call__(self, phone_number):
        if re.fullmatch(self.phone_number_pattern, phone_number) is None:
            raise ValidationError(self.error_message)


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
        validators=[PhoneNumberValidator("Please enter a valid phone number")],
    )

    registrar_email = forms.CharField(
        label="Email address",
        help_text="We will use this email address to confirm your application",
        validators=[EmailValidator("Please enter a valid email address")],
    )

    def __init__(self, *args, **kwargs):
        self.change = kwargs.pop("change", None)
        super().__init__(*args, **kwargs)

        registrar_organisations = [("", "")] + list(
            (f"registrar-{registrar.id}", registrar.name)
            for registrar in Registrar.objects.all()
        )

        self.fields["registrar_organisation"].choices = registrar_organisations

        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Organisation name</h2>'),
                Field.text("registrar_organisation"),
            ),
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Contact details</h2>'),
                Field.text("registrar_name", field_width=20),
                Field.text("registrar_phone", field_width=20),
                Field.text("registrar_email"),
            ),
            Button("submit", "Submit"),
        )
        if self.change:
            self.helper.layout.fields.append(
                Button.secondary("back_to_answers", "Back to answers")
            )


class RegistrantTypeForm(forms.Form):
    registrant_types = [Choice(*item) for item in RegistrantTypeChoices.choices]
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


class DomainForm(forms.Form):
    domain_name = forms.CharField(
        label="Enter the .gov.uk domain name",
    )
    domain_input_regexp = re.compile(
        "^[a-z][a-z0-9-]+[a-z0-9](\\.gov\\.uk)?$"
    )  # based on RFC1035

    def clean_domain_name(self) -> str:
        domain_typed: str = self.cleaned_data["domain_name"].strip()
        matched: Optional[re.Match] = re.fullmatch(
            self.domain_input_regexp, domain_typed
        )
        if matched is not None:
            if ".gov.uk" not in domain_typed:
                domain_typed = domain_typed + ".gov.uk"
        else:
            raise ValidationError("Please enter a valid domain name")

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
                    "The .gov.uk domain name you submit will be subject to approval from the Domains Team."
                ),
            ),
            Button("submit", "Continue"),
        )
        if self.change:
            self.helper.layout.fields.append(
                Button.secondary("back_to_answers", "Back to answers")
            )


class DomainConfirmationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.domain_name = kwargs.pop("domain_name", None)
        super().__init__(*args, **kwargs)
        self.fields["domain_confirmation"] = forms.ChoiceField(
            label=f"Is {self.domain_name} the correct domain name?",
            choices=(("yes", "Yes, I confirm"), ("no", "No, I want to change it")),
            widget=forms.RadioSelect,
            help_text="The Domains Team will review the domain name and make a decision on whether to approve or reject it.",
            error_messages={"required": "Please answer Yes or No"},
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
        label="",
        help_text="""You must provide the formal legal name of your registrant’s
        organisation. the Domains Team will reject applications if the
        registrant’s organisation name does not match official records or is
        spelled incorrectly.""",
    )

    registrant_full_name = forms.CharField(
        label="Full name",
    )

    registrant_phone = forms.CharField(
        label="Telephone number",
        validators=[PhoneNumberValidator("Please enter a valid phone number")],
    )

    registrant_email = forms.CharField(
        label="Email address",
        validators=[EmailValidator("Please enter a valid email address")],
    )

    def __init__(self, *args, **kwargs):
        self.change = kwargs.pop("change", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Organisation name</h2>'),
                Field.text("registrant_organisation"),
            ),
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Contact details</h2>'),
                DomainsHTML.p(
                    "We are collecting the registrant’s personal contact details to confirm their identity."
                ),
                Field.text("registrant_full_name", field_width=20),
                Field.text("registrant_phone", field_width=20),
                Field.text("registrant_email"),
                DomainsHTML.warning(
                    "You must not publish personal contact details on the registry."
                ),
            ),
            Button("submit", "Continue"),
        )
        if self.change:
            self.helper.layout.fields.append(
                Button.secondary("back_to_answers", "Back to answers")
            )


class RegistryDetailsForm(forms.Form):
    registrant_role = forms.CharField(
        label="Role name",
    )

    registrant_contact_email = forms.CharField(
        label="Email address",
        help_text="Use a role-based email address, like clerk@[yourorganisation].gov.uk",
        validators=[EmailValidator("Please enter a valid email address")],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_size = Size.SMALL
        self.helper.layout = Layout(
            Fieldset(
                DomainsHTML('<h2 class="govuk-heading-m">Registrant role</h2>'),
                Field.text("registrant_role", field_width=20),
            ),
            Fieldset(
                DomainsHTML(
                    '<h2 class="govuk-heading-m">Registrant contact details</h2>'
                ),
                Field.text("registrant_contact_email"),
            ),
            Button("submit", "Continue"),
        )


class WrittenPermissionForm(forms.Form):
    CHOICES = (
        Choice("yes", "Yes"),
        Choice("no", "No"),
    )

    written_permission = forms.ChoiceField(
        label="",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Please answer Yes or No"},
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
        error_messages={"required": "Please answer Yes or No"},
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
            help_text=f"If {self.domain_name} does not meet the domain naming rules, it could still be approved if it has ministerial support. For example, the domain is needed to support the creation of a new government department or body.",
            choices=(("yes", "Yes"), ("no", "No")),
            widget=forms.RadioSelect,
            error_messages={"required": "Please answer Yes or No"},
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
        help_text="We support JPEG, PNG or PDF files. The maximum upload size is %s."
        % filesizeformat(settings.MAX_UPLOAD_SIZE),
        error_messages={"required": "Choose the file you want to upload."},
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
        if (
            file is not None
            and file.content_type.split("/")[1] in settings.CONTENT_TYPES
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
                "Wrong file format. Please upload an image or PDF."
            )

        return file


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
        label="Why do you want a .gov.uk domain name?",
        help_text="Tell us what you plan to use the .gov.uk domain name for. Select one option",
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
