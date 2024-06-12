from django.shortcuts import redirect
from django.urls import reverse_lazy


class SessionExpiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Don't check for session for these paths
        print(">", request.path)
        if request.path in [
            reverse_lazy("start"),
            reverse_lazy("start_session"),
            reverse_lazy("success"),
            reverse_lazy("registrar_details"),
        ]:
            return None
        # also add admin views

        # Check if the session has expired
        if request.session.get("registration_data") is None:
            return redirect("start")

        return None
