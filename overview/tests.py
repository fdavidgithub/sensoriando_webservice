import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from overview.views import getCountry, readCookie


class GetCountryTests(SimpleTestCase):
    def test_returns_none_unchanged(self):
        self.assertIsNone(getCountry(None))

    def test_skips_items_without_account(self):
        result = getCountry([{"thing": "t1", "account": None}])
        self.assertEqual(result, [{"thing": "t1", "account": None}])

    def test_keeps_nr_placeholder_without_converting(self):
        result = getCountry([{"thing": "t1", "account": {"country": "NR"}}])
        self.assertEqual(result[0]["account"]["country"], "NR")

    @patch('overview.views.pycountry')
    def test_converts_known_country_code(self, mock_pycountry):
        mock_pycountry.countries.get.return_value = MagicMock(name="Brazil")
        mock_pycountry.countries.get.return_value.name = "Brazil"

        result = getCountry([{"thing": "t1", "account": {"country": "BR"}}])

        mock_pycountry.countries.get.assert_called_once_with(alpha_2="BR")
        self.assertEqual(result[0]["account"]["country"], "Brazil")


def _request_with_cookie(payload):
    return SimpleNamespace(COOKIES={"setFilterHome": json.dumps(payload)})


class ReadCookieTests(SimpleTestCase):
    def test_returns_none_without_cookie(self):
        request = SimpleNamespace(COOKIES={})
        self.assertIsNone(readCookie(request))

    def test_keeps_nr_placeholder_without_crashing(self):
        request = _request_with_cookie({"country": "NR"})

        result = readCookie(request)

        self.assertEqual(result["country"], "NR")

    @patch('overview.views.pycountry')
    def test_converts_recognized_country_name_to_alpha2(self, mock_pycountry):
        mock_pycountry.countries.get.return_value = SimpleNamespace(alpha_2="BR")
        request = _request_with_cookie({"country": "Brazil"})

        result = readCookie(request)

        mock_pycountry.countries.get.assert_called_once_with(name="Brazil")
        self.assertEqual(result["country"], "BR")

    @patch('overview.views.pycountry')
    def test_unrecognized_country_name_does_not_crash(self, mock_pycountry):
        mock_pycountry.countries.get.return_value = None
        request = _request_with_cookie({"country": "Nonexistentland"})

        result = readCookie(request)

        self.assertEqual(result["country"], "Nonexistentland")
