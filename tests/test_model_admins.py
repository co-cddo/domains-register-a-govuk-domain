import datetime
import zoneinfo

from django.test import TestCase

from request_a_govuk_domain.request.admin.model_admins import convert_to_local_time


class ModelAdminTestCase(TestCase):
    def test_bst_time_is_converted_correctly(self):
        """
        Zero GMT should be converted to 1AM local time as we are in BST
        :return:
        """
        bst_date = datetime.datetime(
            2024, 5, 1, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="GMT")
        )
        self.assertEqual("01 May 2024 01:00:00 AM", convert_to_local_time(bst_date))

    def test_gmt_time_is_converted_correctly(self):
        """
        Zero GMT should not be converted as the time zone is GMT in November
        :return:
        """
        gmt_date = datetime.datetime(
            2024, 11, 1, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="GMT")
        )
        self.assertEqual("01 Nov 2024 00:00:00 AM", convert_to_local_time(gmt_date))
