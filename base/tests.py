from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.db.models.functions import Coalesce
from django.test import SimpleTestCase

from base.legacy_tables import Thingssensors
from base.models import (
    get_thing_account,
    get_thing_sensors_with_display_name,
    resolve_account_display,
)


class ThingssensorsSchemaTests(SimpleTestCase):
    def test_name_field_is_nullable_charfield(self):
        field = Thingssensors._meta.get_field('name')

        self.assertEqual(field.get_internal_type(), 'CharField')
        self.assertEqual(field.max_length, 30)
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_channel_field_is_required_integer(self):
        field = Thingssensors._meta.get_field('channel')

        self.assertEqual(field.get_internal_type(), 'IntegerField')
        self.assertFalse(field.null)


class GetThingSensorsWithDisplayNameTests(SimpleTestCase):
    @patch('base.models.ThingsSensorsModel.objects')
    def test_filters_by_thing_and_annotates_display_name(self, mock_objects):
        mock_filtered = MagicMock()
        mock_objects.filter.return_value = mock_filtered
        mock_annotated = MagicMock()
        mock_filtered.annotate.return_value = mock_annotated

        result = get_thing_sensors_with_display_name(42)

        mock_objects.filter.assert_called_once_with(id_thing=42)
        annotate_kwargs = mock_filtered.annotate.call_args.kwargs
        self.assertIsInstance(annotate_kwargs['display_name'], Coalesce)
        self.assertEqual(result, mock_annotated)


class GetThingAccountTests(SimpleTestCase):
    @patch('base.models.AccountsModel.objects')
    def test_filters_by_thing_and_returns_first_match(self, mock_objects):
        mock_filtered = MagicMock()
        mock_objects.filter.return_value = mock_filtered
        mock_related = MagicMock()
        mock_filtered.select_related.return_value = mock_related
        expected_account = SimpleNamespace(id=7)
        mock_related.first.return_value = expected_account

        result = get_thing_account(99)

        mock_objects.filter.assert_called_once_with(accountsthings__id_thing=99)
        mock_filtered.select_related.assert_called_once_with('id_plan')
        self.assertEqual(result, expected_account)


class ResolveAccountDisplayTests(SimpleTestCase):
    def test_returns_defaults_when_no_account(self):
        result = resolve_account_display(None)

        self.assertEqual(result, {
            "is_public": True,
            "city": "não registrado",
            "state": "",
            "country": "NR",
        })

    def test_returns_account_values_when_present(self):
        account = SimpleNamespace(
            id_plan=SimpleNamespace(ispublic=False),
            city="Curitiba",
            state="PR",
            country="BR",
        )

        result = resolve_account_display(account)

        self.assertEqual(result, {
            "is_public": False,
            "city": "Curitiba",
            "state": "PR",
            "country": "BR",
        })
