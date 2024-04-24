from django.test import SimpleTestCase, override_settings, Client
from django.urls import path
import logging
import request_a_govuk_domain


def error_view(request):
    raise Exception("Internal Server Error")


urlpatterns = [
    path("500/", error_view),
]


@override_settings(
    ROOT_URLCONF="request_a_govuk_domain.urls",
)
class ServiceErrorHandlerTests(SimpleTestCase):
    def setUp(self):
        request_a_govuk_domain.urls.urlpatterns.extend(urlpatterns)
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_handler_renders_template_response(self):
        self.client.raise_request_exception = False
        response = self.client.get("/500/")
        self.assertContains(
            response, "Sorry, there is a problem with the service", status_code=500
        )
        self.assertTemplateUsed(response, "500.html")

    # def test_405(self):
    #     response = self.client.get("/minister/")
    #     self.assertContains(
    #         response, "Method not allowed", status_code=405
    #     )
    #     self.assertTemplateUsed(response, "405.html")

    def test_404(self):
        response = self.client.get("/does-not-exist")
        self.assertContains(response, "Page not found", status_code=404)
        self.assertTemplateUsed(response, "404.html")

    def test_403(self):
        self.client = Client(enforce_csrf_checks=True)
        response = self.client.post("minister/", {})
        self.assertContains(response, "Not authorised", status_code=403)
        self.assertTemplateUsed(response, "403.html")
