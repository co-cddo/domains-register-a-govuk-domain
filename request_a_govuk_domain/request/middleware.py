from django.shortcuts import redirect
from django.urls import reverse


class FormProgressMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if self.is_valid_start_path(request.path):
            return response
        if self.is_valid_progress(request):
            return response
        return redirect("start")  # Redirect to start page if progress is invalid

    def is_valid_start_path(self, path: str):
        if path == reverse("start"):
            return True
        if path.startswith("/admin"):
            return True
        return False

    def is_valid_progress(self, request):
        if request.path == reverse("success"):
            return True
        if request.session.get("registration_data") is None:
            return False
        for key in request.session.get("registration_data"):
            if key not in [
                "applicant_email",
                "applicant_name",
                "applicant_phone",
                "domain_name",
                "domain_purpose",
                "registrant_contact_email",
                "registrant_contact_phone",
                "registrant_email_address",
                "registrant_full_name",
                "registrant_organisation_name",
                "registrant_phone",
                "registrant_role",
                "registrant_type",
                "registrar_organisation",
                "written_permission",
            ]:
                # A key in the session data is unknown. So go back to the beginning
                request.session["registration_data"] = {}
                return False
        return True
