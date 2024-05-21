import unittest
from django.test import TestCase

from request_a_govuk_domain.request.utils import route_number


CENTRAL_GOV_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "central_government",
}
# CENTRAL_GOV_RT = {"primary": 2}
NDPB_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "ndpb",
}
# NDPB_RT = {"primary": 2}

CENTRAL_GOV_WEBSITE_EMAIL_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "central_government",
    "domain_purpose": "website-email",
}
# CENTRAL_GOV_WEBSITE_EMAIL_RT = {"primary": 2, "secondary": 7}
NDPB_WEBSITE_EMAIL_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "ndpb",
    "domain_purpose": "website-email",
}
# NDPB_WEBSITE_EMAIL_RT = {"primary": 2, "secondary": 7}

CENTRAL_GOV_EMAIL_ONLY_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "central_government",
    "domain_purpose": "email-only",
}
# CENTRAL_GOV_EMAIL_ONLY_RT = {"primary": 2, "secondary": 5}
NDPB_EMAIL_ONLY_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "ndpb",
    "domain_purpose": "email-only",
}
# NDPB_EMAIL_ONLY_RT = {"primary": 2, "secondary": 5}

# Using 'blah-blah' as the purpose here strays into testing the implementation rather than
# the behaviour but we do really want to get route 6 back if the purpose is anything other
# then email or website/email, so it's a sensible check
CENTRAL_GOV_OTHER_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "central_government",
    "domain_purpose": "blah-blah",
}
# CENTRAL_GOV_OTHER_RT = {"primary": 2, "secondary": 6}
NDPB_OTHER_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "ndpb",
    "domain_purpose": "blah-blah",
}
# NDPB_OTHER_RT = {"primary": 2, "secondary": 6}

# Route 9 is only where a CG/NDPB's domain purpose is not email or website/email
# AND they do not have written permission
CENTRAL_GOV_OTHER_NO_PERM_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "central_government",
    "domain_purpose": "blah-blah",
    "written_permission": "no",
}
# CENTRAL_GOV_OTHER_NO_PERM_RT = {"primary": 2, "secondary": 6, "tertiary": 9}
NDPB_OTHER_NO_PERM_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "ndpb",
    "domain_purpose": "blah-blah",
    "written_permission": "no",
}
# NDPB_OTHER_NO_PERM_RT = {"primary": 2, "secondary": 6, "tertiary": 9}

# When a CG/NDPB has senior support for domain, it's route 8, irrespective
# of whether they have written permission
CENTRAL_GOV_OTHER_SENIOR_REQUEST_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "central_government",
    "domain_purpose": "blah-blah",
    "written_permission": "no",
}
CENTRAL_GOV_OTHER_SENIOR_REQUEST_RT = {"primary": 2, "secondary": 6, "tertiary": 8}
NDPB_OTHER_SENIOR_REQUEST_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "ndpb",
    "domain_purpose": "blah-blah",
    "written_permission": "no",
}
NDPB_OTHER_SENIOR_REQUEST_RT = {"primary": 2, "secondary": 6, "tertiary": 8}

PARISH_COUNCIL_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "parish_council",
}
PARISH_COUNCIL_RT = {"primary": 2}
VILLAGE_COUNCIL_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "village_council",
}
VILLAGE_COUNCIL_RT = {"primary": 2}

PARISH_COUNCIL_NO_DOMAIN_CONFIRMATION_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "parish_council",
    "domain_confirmation": "no",
}

PARISH_COUNCIL_NO_DOMAIN_CONFIRMATION_RT = {"primary": 2, "secondary": 12}
VILLAGE_COUNCIL_NO_DOMAIN_CONFIRMATION_SD = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
    "registrant_type": "village_council",
    "domain_confirmation": "no",
}
VILLAGE_COUNCIL_NO_DOMAIN_CONFIRMATION_RT = {"primary": 2, "secondary": 12}


OTHER_REGISTRANT_SD_TEMPLATE = {
    "registrar_organisation": "registrar-3",
    "registrar_name": "John Smith",
    "registrar_phone": "01692 111 222",
    "registrar_email": "john.smith@aregistrar.co.uk",
}
OTHER_REGISTRANT_SDS = [
    {"registrant_type": registrant_type}.update(OTHER_REGISTRANT_SD_TEMPLATE)
    for registrant_type in [
        "local_authority",
        "fire_service",
        "combined_authority",
        "pcc",
        "joint_authority",
        "joint_committee",
        "representing_psb",
        "representing_profession",
    ]
]
OTHER_REGISTRANT_RT = {"primary": 3}


class TestRouteNumber(unittest.TestCase):

    def setUp(self):
        pass

    def test_central_gov_no_other_data(self):
        route = route_number(CENTRAL_GOV_SD)
        self.assertDictEqual(route, {"primary": 2})

    def test_ndpb_no_other_data(self):
        route = route_number(NDPB_SD)
        self.assertDictEqual(route, {"primary": 2})

    def test_central_gov_domain_purpose_email(self):
        route = route_number(CENTRAL_GOV_EMAIL_ONLY_SD)
        self.assertDictEqual(route, {"primary": 2, "secondary": 5})

    def test_ndpb_domain_purpose_email(self):
        route = route_number(NDPB_EMAIL_ONLY_SD)
        self.assertDictEqual(route, {"primary": 2, "secondary": 5})

    def test_central_gov_domain_purpose_website_email(self):
        route = route_number(CENTRAL_GOV_WEBSITE_EMAIL_SD)
        self.assertDictEqual(route, {"primary": 2, "secondary": 6, "tertiary": 9})

    def test_ndpb_domain_purpose_website_email(self):
        route = route_number(NDPB_WEBSITE_EMAIL_SD)
        self.assertDictEqual(route, {"primary": 2, "secondary": 7})

    def test_central_gov_domain_purpose_other(self):
        route = route_number(CENTRAL_GOV_OTHER_SD)
        self.assertDictEqual(route, {"primary": 2, "secondary": 7})

    def test_ndpb_domain_purpose_other(self):
        route = route_number(NDPB_OTHER_SD)
        self.assertDictEqual(route, NDPB_OTHER_RT)

    def test_central_gov_domain_purpose_other_no_permission(self):
        route = route_number(CENTRAL_GOV_OTHER_NO_PERM_SD)
        self.assertDictEqual(route, CENTRAL_GOV_OTHER_NO_PERM_RT)

    def test_ndpb_domain_purpose_other_no_permission(self):
        route = route_number(NDPB_OTHER_NO_PERM_SD)
        self.assertDictEqual(route, NDPB_OTHER_NO_PERM_RT)

    def test_central_gov_domain_purpose_other_yes_permission(self):
        route = route_number(CENTRAL_GOV_OTHER_NO_PERM_SD)
        self.assertDictEqual(route, CENTRAL_GOV_OTHER_NO_PERM_RT)

    def test_ndpb_domain_purpose_other_yes_permission(self):
        route = route_number(NDPB_OTHER_NO_PERM_SD)
        self.assertDictEqual(route, NDPB_OTHER_NO_PERM_RT)
