from django.urls import reverse_lazy
from django.views.generic import FormView
from ..forms.registrant_type import RegistrantTypeForm


class RegistrantTypeView(FormView):
    template_name = "registrant_type.html"
    form_class = RegistrantTypeForm
    success_url = reverse_lazy("confirm")

    def form_valid(self, form):
        registration_data = self.request.session.get("registration_data", {})
        registration_data["registrant_type"] = form.cleaned_data["registrant_type"]
        self.request.session["registration_data"] = registration_data
        if form.cleaned_data["registrant_type"] == "none":
            self.success_url = reverse_lazy("registrant_type_fail")
        return super().form_valid(form)
