from django.test import SimpleTestCase

from base.legacy_tables import Thingssensors


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
