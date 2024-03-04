"""
WSGI config for request_a_govuk_domain project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import pathlib

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "request_a_govuk_domain.settings")

application = get_wsgi_application()
from whitenoise import WhiteNoise

static_path = pathlib.Path(__file__).parent.joinpath("static")
application = WhiteNoise(application, root=static_path.absolute())
application.add_files(static_path.joinpath("images"), prefix="assets/images/")
application.add_files(static_path.joinpath("fonts"), prefix="assets/fonts/")
