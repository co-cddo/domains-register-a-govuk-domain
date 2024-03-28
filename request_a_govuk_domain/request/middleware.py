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
        if path.startswith("/media"):
            return True
        return False

    def is_valid_progress(self, request):
        if request.path in [reverse("success"), reverse("registrar_details")]:
            return True
        if request.session.get("registration_data") is None:
            return False
        # Add more here as the data model is finalised
        return True
