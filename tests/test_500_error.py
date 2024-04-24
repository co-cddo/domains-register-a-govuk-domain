from django.test import SimpleTestCase, override_settings
from django.urls import path
import logging
import request_a_govuk_domain


def error_view(request):
    raise Exception("Internal Server Error")


urlpatterns = [
    path("500/", error_view),
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


@override_settings(
    ROOT_URLCONF="request_a_govuk_domain.urls",
    MIDDLEWARE=MIDDLEWARE,
)
class ServiceFailureErrorHandlerTests(SimpleTestCase):
    def setUp(self):
        request_a_govuk_domain.urls.urlpatterns.extend(urlpatterns)

    def test_handler_renders_template_response(self):
        self.client.raise_request_exception = False
        logging.disable(logging.ERROR)
        response = self.client.get("/500/")
        logging.disable(logging.NOTSET)
        self.assertContains(
            response, "Sorry, there is a problem with the service", status_code=500
        )
        self.assertTemplateUsed(response, "500.html")
