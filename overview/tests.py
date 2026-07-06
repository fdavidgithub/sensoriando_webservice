from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from overview.views import getCountry


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
