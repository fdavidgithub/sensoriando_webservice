from unittest.mock import MagicMock, patch

from django.db.models import Q
from django.test import SimpleTestCase

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
