from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.db.models import Q
from django.test import SimpleTestCase

from api.serializers import DataThingsSerializer
from api.views import PublicThingsViewSets


class PublicThingsGetQuerysetTests(SimpleTestCase):
    @patch('api.views.ThingsModel.objects')
    def test_includes_things_without_account_or_with_public_active_account(self, mock_objects):
        mock_filtered = MagicMock()
        mock_objects.filter.return_value = mock_filtered
        mock_filtered.distinct.return_value = mock_filtered

        view = PublicThingsViewSets()
        result = view.get_queryset(params={})

        expected_q = (
            Q(accountsthings__isnull=True) |
            Q(accountsthings__id_account__status=True,
              accountsthings__id_account__id_plan__ispublic=True)
        )
        called_args, _ = mock_objects.filter.call_args
        self.assertEqual(called_args[0], expected_q)
        mock_filtered.distinct.assert_called_once()
        self.assertEqual(result, mock_filtered)


class DataThingsSerializerGetAccountTests(SimpleTestCase):
    @patch('api.serializers.get_thing_account')
    def test_returns_fallback_when_no_account(self, mock_get_thing_account):
        mock_get_thing_account.return_value = None
        obj = SimpleNamespace(id=1, name="thing-1", uuid="uuid-1")

        result = DataThingsSerializer().get_account(obj)

        mock_get_thing_account.assert_called_once_with(obj)
        self.assertEqual(result, {
            "username": None,
            "city": "não registrado",
            "state": "",
            "country": "NR",
        })

    @patch('api.serializers.get_thing_account')
    def test_returns_account_data_when_account_exists(self, mock_get_thing_account):
        mock_get_thing_account.return_value = SimpleNamespace(
            username="acc1", city="Curitiba", state="PR", country="BR"
        )
        obj = SimpleNamespace(id=1, name="thing-1", uuid="uuid-1")

        result = DataThingsSerializer().get_account(obj)

        self.assertEqual(result, {
            "username": "acc1",
            "city": "Curitiba",
            "state": "PR",
            "country": "BR",
        })


class DataThingsSerializerGetSensorsTests(SimpleTestCase):
    @patch('api.serializers.get_thing_sensors_with_display_name')
    def test_returns_id_and_resolved_display_name(self, mock_get_thing_sensors):
        mock_get_thing_sensors.return_value = [
            SimpleNamespace(id_sensor_id=10, display_name="Custom Name"),
            SimpleNamespace(id_sensor_id=11, display_name="Temperature"),
        ]
        obj = SimpleNamespace(id=1)

        result = DataThingsSerializer().get_sensors(obj)

        mock_get_thing_sensors.assert_called_once_with(obj)
        self.assertEqual(result, [
            {"id": 10, "name": "Custom Name"},
            {"id": 11, "name": "Temperature"},
        ])


class DataThingsSerializerThingFieldsTests(SimpleTestCase):
    def test_get_thing_returns_name_from_obj(self):
        obj = SimpleNamespace(name="thing-1", uuid="uuid-1")
        self.assertEqual(DataThingsSerializer().get_thing(obj), "thing-1")

    def test_get_uuid_returns_uuid_from_obj(self):
        obj = SimpleNamespace(name="thing-1", uuid="uuid-1")
        self.assertEqual(DataThingsSerializer().get_uuid(obj), "uuid-1")
