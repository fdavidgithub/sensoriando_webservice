from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import FieldError
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.test import SimpleTestCase

from api.serializers import DataThingsSerializer
from api.views import PublicThingsViewSets, PrivateThingsViewSets, DataViewSets
from base.models import ThingsModel


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


class PrivateThingsGetQuerysetTests(SimpleTestCase):
    @patch('api.views.AccountsModel.objects')
    @patch('api.views.ThingsModel.objects')
    def test_filters_things_via_accountsthings_relation(self, mock_things_objects, mock_accounts_objects):
        mock_account = SimpleNamespace(id=5)
        mock_accounts_objects.get.return_value = mock_account

        mock_filtered = MagicMock()
        mock_things_objects.filter.return_value = mock_filtered
        mock_filtered.distinct.return_value = mock_filtered

        view = PrivateThingsViewSets()
        result = view.get_queryset(params={}, user="someuser")

        mock_accounts_objects.get.assert_called_once_with(username="someuser")
        called_kwargs = mock_things_objects.filter.call_args.kwargs
        self.assertEqual(called_kwargs, {
            "accountsthings__id_account__status": True,
            "accountsthings__id_account__id_plan__ispublic": False,
            "accountsthings__id_account": mock_account,
        })
        mock_filtered.distinct.assert_called_once()
        self.assertEqual(result, mock_filtered)


class GetFiltersFieldPathTests(SimpleTestCase):
    def _assert_filters_resolve_against_thingsmodel(self, filters):
        for key, filter_func in filters.items():
            q = filter_func("some-value")
            try:
                ThingsModel.objects.filter(q)
            except FieldError as e:
                self.fail("filter '%s' produced a Q object with an invalid "
                          "field path for ThingsModel: %s" % (key, e))

    def test_public_things_filters_resolve_against_thingsmodel(self):
        view = PublicThingsViewSets()
        self._assert_filters_resolve_against_thingsmodel(view.get_filters())

    def test_private_things_filters_resolve_against_thingsmodel(self):
        view = PrivateThingsViewSets()
        self._assert_filters_resolve_against_thingsmodel(view.get_filters())


class DataViewSetsSensorResolutionTests(SimpleTestCase):
    @patch('api.views.AccountsThingsModel.objects')
    @patch('api.views.ThingsSensorsModel.objects')
    def test_resolves_sensor_by_coalesced_display_name(self, mock_ts_objects, mock_accountsthings_objects):
        mock_annotated = MagicMock()
        mock_ts_objects.annotate.return_value = mock_annotated
        mock_thingsensor = SimpleNamespace(pk=42)
        mock_annotated.get.return_value = mock_thingsensor

        # short-circuit the rest of get_queryset via the (still isPublic=False,
        # thus unchanged) checkPublic gate
        mock_filtered = MagicMock()
        mock_filtered.__bool__.return_value = False
        mock_filtered.exists.return_value = False
        mock_accountsthings_objects.filter.return_value = mock_filtered

        view = DataViewSets()
        view.isPublic = False
        request = SimpleNamespace(data={"thing": "uuid-1", "sensor": "custom-name"})

        view.get_queryset(request)

        annotate_kwargs = mock_ts_objects.annotate.call_args.kwargs
        self.assertIsInstance(annotate_kwargs['display_name'], Coalesce)

        mock_annotated.get.assert_called_once_with(
            id_thing__uuid="uuid-1",
            display_name="custom-name",
        )


class DataViewSetsCheckPublicGateTests(SimpleTestCase):
    @patch('api.views.ThingsModel.objects')
    def test_public_gate_allows_things_without_account(self, mock_things_objects):
        mock_filtered = MagicMock()
        mock_things_objects.filter.return_value = mock_filtered
        mock_filtered2 = MagicMock()
        mock_filtered.filter.return_value = mock_filtered2
        mock_filtered2.exists.return_value = False

        view = DataViewSets()
        view.isPublic = True
        # no "sensor" key: skips the ThingsSensorsModel lookup entirely
        request = SimpleNamespace(data={"thing": "uuid-1"})

        result = view.get_queryset(request)

        mock_things_objects.filter.assert_called_once_with(uuid="uuid-1")

        expected_q = (
            Q(accountsthings__isnull=True) |
            Q(accountsthings__id_account__status=True,
              accountsthings__id_account__id_plan__ispublic=True)
        )
        filter_call_args, _ = mock_filtered.filter.call_args
        self.assertEqual(filter_call_args[0], expected_q)
        mock_filtered2.exists.assert_called_once()
        self.assertIsNone(result)

    @patch('api.views.AccountsThingsModel.objects')
    def test_private_gate_behavior_is_unchanged(self, mock_accountsthings_objects):
        mock_filtered = MagicMock()
        mock_accountsthings_objects.filter.return_value = mock_filtered
        mock_filtered.__bool__.return_value = False
        mock_filtered.exists.return_value = False

        view = DataViewSets()
        view.isPublic = False
        request = SimpleNamespace(data={"thing": "uuid-1"})

        result = view.get_queryset(request)

        mock_accountsthings_objects.filter.assert_called_once_with(
            id_thing__uuid="uuid-1",
            id_account__id_plan__ispublic=False,
        )
        mock_filtered.exists.assert_called_once()
        self.assertIsNone(result)
