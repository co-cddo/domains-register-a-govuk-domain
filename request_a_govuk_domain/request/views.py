import logging
import random
import string
from datetime import datetime

from django.core.exceptions import BadRequest
from django.db import transaction
from django.http import HttpResponse, HttpRequest, FileResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import FormView

from .constants import NOTIFY_TEMPLATE_ID_MAP
from .db import save_data_in_database
from .forms import (
    DomainConfirmationForm,
    ExemptionForm,
    UploadForm,
    RegistrarDetailsForm,
    RegistrantTypeForm,
    DomainPurposeForm,
    DomainForm,
    MinisterForm,
    RegistrantDetailsForm,
    RegistryDetailsForm,
    WrittenPermissionForm,
    ConfirmationForm,
)
from .models.organisation import Registrar, RegistrantTypeChoices
from .models.storage_util import select_storage
from .utils import (
    handle_uploaded_file,
    add_to_session,
    remove_from_session,
    route_number,
    send_email,
    route_specific_email_template,
    personalisation,
    get_registration_data,
)

REGISTRATION_DATA = "registration_data"

# Name of the cookie holding the application reference
APPLICATION_REFERENCE = "application_reference"

logger = logging.getLogger(__name__)


class StartView(TemplateView):
    template_name = "start.html"


class StartSessionView(RedirectView):
    pattern_name = "registrar_details"

    def setup(self, request, *args, **kwargs):
        # User has clicked the green button, so they're
        # starting a new journey. Therefore delete the session data
        # so that no previous answer is shown in the new journey.
        request.session.pop(REGISTRATION_DATA, None)
        request.session.pop(APPLICATION_REFERENCE, None)
        return super().setup(request, *args, **kwargs)


class CookiesPageView(TemplateView):
    template_name = "cookies.html"


class AccessibilityView(TemplateView):
    template_name = "accessibility.html"


class TermsAndConditionsView(TemplateView):
    template_name = "terms.html"


class PrivacyPolicyPageView(TemplateView):
    template_name = "privacy.html"


class RegistrarDetailsView(FormView):
    template_name = "registrar_details.html"
    form_class = RegistrarDetailsForm
    success_url = reverse_lazy("registrant_type")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        session_data = self.request.session.get(REGISTRATION_DATA)
        if session_data is not None:
            initial["registrar_organisation"] = session_data.get(
                "registrar_organisation", ""
            )
            initial["registrar_name"] = session_data.get("registrar_name", "")
            initial["registrar_phone"] = session_data.get("registrar_phone", "")
            initial["registrar_email"] = session_data.get("registrar_email", "")
        return initial

    def form_valid(self, form):
        add_to_session(
            form,
            self.request,
            [
                "registrar_organisation",
                "registrar_name",
                "registrar_phone",
                "registrar_email",
            ],
        )
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = reverse_lazy("confirm")
        return super().form_valid(form)


class RegistrantTypeView(FormView):
    template_name = "registrant_type.html"
    success_url = reverse_lazy("domain")  # TODO: by default should be an error page
    form_class = RegistrantTypeForm

    def get_initial(self):
        session_data = get_registration_data(self.request)
        initial = super().get_initial()
        initial["registrant_type"] = session_data.get("registrant_type", "")
        return initial

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["registrant_type"])
        route = route_number(registration_data).get("primary")
        if route == 1:
            self.success_url = reverse_lazy("domain")
        elif route == 2:
            self.success_url = reverse_lazy("domain_purpose")
        elif route == 3:
            self.success_url = reverse_lazy("written_permission")
        elif route == 4:
            self.success_url = reverse_lazy("registrant_type_fail")
        return super().form_valid(form)


class DomainView(FormView):
    template_name = "domain.html"
    form_class = DomainForm
    success_url = reverse_lazy("domain_confirmation")
    change = False

    def get_initial(self):
        initial = super().get_initial()
        session_data = get_registration_data(self.request)
        initial["domain_name"] = session_data.get("domain_name", "")
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_data = self.request.session.get(REGISTRATION_DATA, {})
        context["route"] = route_number(registration_data)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def form_valid(self, form):
        add_to_session(form, self.request, ["domain_name"])
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = reverse_lazy("confirm")
        return super().form_valid(form)


class DomainConfirmationView(FormView):
    template_name = "domain_confirmation.html"
    form_class = DomainConfirmationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        session = self.request.session.get(REGISTRATION_DATA, {})
        kwargs["domain_name"] = session.get("domain_name")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[REGISTRATION_DATA] = self.request.session.get(REGISTRATION_DATA, {})
        return context

    def get_initial(self):
        initial = super().get_initial()
        session_data = get_registration_data(self.request)
        initial["domain_confirmation"] = session_data.get("domain_confirmation", "")
        return initial

    def form_valid(self, form):
        session_data = add_to_session(form, self.request, ["domain_confirmation"])
        route = route_number(session_data)
        if route.get("secondary") == 12:
            self.success_url = reverse_lazy("domain")
        elif route.get("primary") == 1 or route.get("primary") == 3:
            self.success_url = reverse_lazy("registrant_details")
        else:
            self.success_url = reverse_lazy("minister")

        return super().form_valid(form)


class RegistrantDetailsView(FormView):
    template_name = "registrant_details.html"
    form_class = RegistrantDetailsForm
    success_url = reverse_lazy("registry_details")
    change = False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["change"] = getattr(self, "change")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_data = self.request.session.get(REGISTRATION_DATA, {})
        context["route"] = route_number(registration_data)
        return context

    def get_initial(self):
        initial = super().get_initial()
        session_data = get_registration_data(self.request)
        initial["registrant_organisation"] = session_data.get(
            "registrant_organisation", ""
        )
        initial["registrant_full_name"] = session_data.get("registrant_full_name", "")
        initial["registrant_phone"] = session_data.get("registrant_phone", "")
        initial["registrant_email"] = session_data.get("registrant_email", "")
        return initial

    def form_valid(self, form):
        add_to_session(
            form,
            self.request,
            [
                "registrant_organisation",
                "registrant_full_name",
                "registrant_phone",
                "registrant_email",
            ],
        )
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = reverse_lazy("confirm")
        return super().form_valid(form)


class RegistryDetailsView(FormView):
    template_name = "registry_details.html"
    form_class = RegistryDetailsForm
    success_url = reverse_lazy("confirm")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        registrant_type = get_registration_data(self.request)["registrant_type"]
        if registrant_type == "parish_council":
            kwargs["hint_email"] = "clerk@[yourorganisation].gov.uk"
        else:
            kwargs["hint_email"] = "itsupport@[yourorganisation].gov.uk"
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        session_data = get_registration_data(self.request)
        initial["registrant_role"] = session_data.get("registrant_role", "")
        initial["registrant_contact_email"] = session_data.get(
            "registrant_contact_email", ""
        )
        return initial

    def form_valid(self, form):
        add_to_session(
            form,
            self.request,
            ["registrant_role", "registrant_contact_email"],
        )
        return super().form_valid(form)


class RegistrantTypeFailView(TemplateView):
    template_name = "registrant_type_fail.html"


class WrittenPermissionView(FormView):
    template_name = "written_permission.html"
    form_class = WrittenPermissionForm
    success_url = reverse_lazy("written_permission_upload")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_data = self.request.session.get(REGISTRATION_DATA, {})
        context["route"] = route_number(registration_data)
        return context

    def get_initial(self):
        initial = super().get_initial()
        session_data = get_registration_data(self.request)
        initial["written_permission"] = session_data.get("written_permission", "")
        return initial

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["written_permission"])
        if registration_data["written_permission"] == "no":
            self.success_url = reverse_lazy("written_permission_fail")

        # if the user has previously uploaded a file, take them to the confirmation directly
        elif (
            registration_data.get("written_permission_file_uploaded_filename")
            is not None
        ):
            self.success_url = reverse_lazy("written_permission_upload_confirm")

        return super().form_valid(form)


class WrittenPermissionFailView(TemplateView):
    template_name = "written_permission_fail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_data = self.request.session.get(REGISTRATION_DATA, {})
        context["route"] = route_number(registration_data)
        return context


class UploadRemoveView(RedirectView):
    page_type = ""  # to be subclassed
    permanent = False
    query_string = True
    pattern_name = ""  # to be subclassed

    def get_redirect_url(self, *args, **kwargs):
        registration_data = self.request.session.get(REGISTRATION_DATA, {})
        if path_to_delete := registration_data.get(
            self.page_type + "_file_uploaded_filename"
        ):
            storage = select_storage()
            if storage.exists(path_to_delete):
                storage.delete(path_to_delete)

        # delete the session data
        remove_from_session(
            self.request.session,
            [
                self.page_type + "_file_uploaded_filename",
                self.page_type + "_file_original_filename",
                self.page_type + "_file_uploaded_url",
            ],
        )

        return super().get_redirect_url(*args, **kwargs)


class ExemptionUploadRemoveView(UploadRemoveView):
    page_type = "exemption"
    pattern_name = "exemption_upload"


class WrittenPermissionUploadRemoveView(UploadRemoveView):
    page_type = "written_permission"
    pattern_name = "written_permission_upload"


class MinisterUploadRemoveView(UploadRemoveView):
    page_type = "minister"
    pattern_name = "minister_upload"


class ConfirmView(TemplateView):
    template_name = "confirm.html"

    def post(self, request):
        """
        Save the form and redirect to the success view.
        :param request:
        :return:
        """
        reference_ = request.session.get(APPLICATION_REFERENCE)
        status = self.save_application_to_database_and_send_confirmation_email(
            reference_, request
        )
        if status:
            return redirect("success")
        else:
            return HttpResponseNotFound()

    @transaction.atomic  # This ensures that any failure during email send will not save data in db either
    def save_application_to_database_and_send_confirmation_email(
        self, reference: str, request: HttpRequest
    ):
        """
        Saves data in the db and sends confirmation email

        :param reference: Application reference
        :param request: request object
        """
        logger.info(f"Saving form {request.session.session_key}")
        status = save_data_in_database(reference, request)
        self.send_confirmation_email(reference, request)
        return status

    def send_confirmation_email(self, reference: str, request) -> None:
        """
        Method to send Confirmation email

        It gets the required personalisation data from request and calls send_email to send the confirmation email

        :param reference: Application reference
        :param request: request object
        """
        registration_data = request.session.get(REGISTRATION_DATA, {})

        # Notify personalisation dictionary to be used in the notify templates
        personalisation_dict = personalisation(reference, registration_data)

        route_specific_email_template_name = route_specific_email_template(
            "confirmation", registration_data
        )

        send_email(
            email_address=registration_data["registrar_email"],
            template_id=NOTIFY_TEMPLATE_ID_MAP[
                route_specific_email_template_name
            ],  # Notify API template id of route specific Confirmation email
            personalisation=personalisation_dict,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Access session data and include it in the context
        registration_data = get_registration_data(self.request)
        context[REGISTRATION_DATA] = registration_data

        # Registrar organisation name: need to look up real name
        registrar_id = int(
            registration_data["registrar_organisation"].split("registrar-", 1)[1]
        )
        context["registrar_name"] = Registrar.objects.get(id=registrar_id).name

        # Registrant type human-readable name
        registrant_types = {
            code: label for code, label in RegistrantTypeChoices.choices
        }
        context["registrant_type"] = registrant_types[
            registration_data["registrant_type"]
        ]
        # Pass the route number as what's on the page depends on it
        context["route"] = route_number(self.request.session.get(REGISTRATION_DATA))
        form = ConfirmationForm({})
        context["form"] = form
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        self.request.session[APPLICATION_REFERENCE] = self.generate_reference()
        return response

    def generate_reference(self) -> str:
        """
        Generate application reference with the following format:
        GOVUK + date in DDMMYYYY + random 4 letter alphabetical characters ( which don't have vowels and Y )
        e.g. 'GOVUK12042024TRFT'

        Returns:
            str: application reference.
        """

        random_letters = [
            letter for letter in string.ascii_uppercase if letter not in "AEIOUY"
        ]
        random_string = "".join(random.choices(random_letters, k=4))
        return "GOVUK" + datetime.today().strftime("%d%m%Y") + random_string


class SuccessView(View):
    def get(self, request):
        if application_reference := request.session.get(APPLICATION_REFERENCE):
            http_response = render(
                request, "success.html", {"reference": application_reference}
            )
            # No need to store it anymore
            # We're finished, so clear the session data
            request.session.pop(REGISTRATION_DATA, None)
            request.session.pop(APPLICATION_REFERENCE, None)
            request.session.modified = True
            return http_response
        raise BadRequest("Invalid data in request")


class ExemptionView(FormView):
    template_name = "exemption.html"
    form_class = ExemptionForm

    def get_initial(self):
        initial = super().get_initial()
        session_data = get_registration_data(self.request)
        initial["exemption"] = session_data.get("exemption", "")
        return initial

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["exemption"])
        exemption = registration_data["exemption"]
        if exemption == "yes":
            self.success_url = reverse_lazy("exemption_upload")
        else:
            self.success_url = reverse_lazy("exemption_fail")
        return super().form_valid(form)


class MinisterView(FormView):
    template_name = "minister.html"
    form_class = MinisterForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        session = self.request.session.get(REGISTRATION_DATA, {})
        kwargs["domain_name"] = session.get("domain_name")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        session_data = get_registration_data(self.request)
        initial["minister"] = session_data.get("minister", "")
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[REGISTRATION_DATA] = self.request.session.get(REGISTRATION_DATA, {})
        return context

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["minister"])
        minister = registration_data["minister"]
        if minister == "yes":
            if registration_data.get("minister_file_uploaded_filename") is not None:
                # if user previously uploaded a file, go to confirm directly
                self.success_url = reverse_lazy("minister_upload_confirm")
            else:
                self.success_url = reverse_lazy("minister_upload")
        else:
            self.success_url = reverse_lazy("registrant_details")
        return super().form_valid(form)


def download_file(request, file_type):
    """
    Utility method to download a file which was temporarily uploaded during the application process.
    :param request: Current request object
    :param file_type:  Type of file to be downloaded
    :return:
    """
    registration_data = get_registration_data(request)
    storage = select_storage()
    file_name = registration_data[f"{file_type}_file_uploaded_filename"]
    if storage.exists(file_name):
        return FileResponse(storage.open(file_name, "rb"))
    return HttpResponseNotFound("Not Found")


class UploadView(FormView):
    page_type = ""
    template_name = ""
    success_url = None
    form_class = UploadForm

    def __init__(self):
        self.success_url = reverse_lazy(f"{self.page_type}_upload_confirm")
        self.template_name = f"{self.page_type}_upload.html"
        return super().__init__()

    def form_valid(self, form):
        saved_filename = handle_uploaded_file(
            self.request.FILES["file"], self.request.session.session_key
        )
        registration_data = self.request.session.get(REGISTRATION_DATA, {})
        registration_data[f"{self.page_type}_file_uploaded_filename"] = saved_filename
        registration_data[f"{self.page_type}_file_uploaded_url"] = select_storage().url(
            saved_filename
        )
        registration_data[
            f"{self.page_type}_file_original_filename"
        ] = self.request.FILES["file"].name
        self.request.session[REGISTRATION_DATA] = registration_data
        if "back_to_answers" in self.request.POST.keys():
            self.success_url = reverse_lazy("confirm")
        return super().form_valid(form)


class UploadConfirmView(TemplateView):
    page_type = ""
    template_name = ""

    def get_context_data(self, **kwargs):
        self.template_name = f"{self.page_type}_upload_confirm.html"
        context = super().get_context_data(**kwargs)
        context[REGISTRATION_DATA] = self.request.session.get(REGISTRATION_DATA, {})
        return context


class ExemptionUploadView(UploadView):
    page_type = "exemption"


class MinisterUploadView(UploadView):
    page_type = "minister"


class WrittenPermissionUploadView(UploadView):
    page_type = "written_permission"


class ExemptionUploadConfirmView(UploadConfirmView):
    page_type = "exemption"


class MinisterUploadConfirmView(UploadConfirmView):
    page_type = "minister"


class WrittenPermissionUploadConfirmView(UploadConfirmView):
    page_type = "written_permission"


class ExemptionFailView(FormView):
    template_name = "exemption_fail.html"

    def get(self, request):
        return render(request, self.template_name)


class DomainPurposeView(FormView):
    template_name = "domain_purpose.html"
    form_class = DomainPurposeForm

    def get_initial(self):
        session_data = get_registration_data(self.request)
        initial = super().get_initial()
        initial["domain_purpose"] = session_data.get("domain_purpose", "")
        return initial

    def form_valid(self, form):
        registration_data = add_to_session(form, self.request, ["domain_purpose"])
        purpose = registration_data["domain_purpose"]
        if purpose == "email-only":
            self.success_url = reverse_lazy("written_permission")
        elif purpose == "website-email":
            self.success_url = reverse_lazy("exemption")
        else:
            self.success_url = reverse_lazy("domain_purpose_fail")

        return super().form_valid(form)


class DomainPurposeFailView(FormView):
    template_name = "domain_purpose_fail.html"

    def get(self, request):
        return render(request, self.template_name)


def service_failure_view(request):
    request.session.pop(REGISTRATION_DATA, None)
    return render(request, "500.html", status=500)


def page_not_found_view(request, exception):
    return render(request, "404.html", status=404)


def security_txt_view(request):
    return redirect("https://www.gov.uk/.well-known/security.txt")


def robots_txt_view(request):
    return HttpResponse("User-agent: *\nDisallow: /\n")


def forbidden_view(request, exception):
    return render(request, "403.html", status=403)


def csrf_failure_view(request, reason=""):
    return render(request, "403.html", status=403)


def bad_request_view(request, exception):
    return render(request, "400.html", status=400)
