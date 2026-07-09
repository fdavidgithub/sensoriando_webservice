import inspect

from django.test import SimpleTestCase

from sensors import views


class ThingDetailsAccountLookupTests(SimpleTestCase):
    def test_does_not_use_unsafe_get_lookup_for_account(self):
        source = inspect.getsource(views.ThingDetails)

        self.assertNotIn("AccountsModel.objects.get(", source)
        self.assertIn("get_thing_account(", source)
