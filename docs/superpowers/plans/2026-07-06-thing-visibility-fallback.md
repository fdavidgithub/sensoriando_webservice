# Thing Visibility Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `Thing` without an associated account becomes public by default and shows up in the public listing and detail page without crashing, and the displayed sensor name resolves to `thingssensors.name` with a fallback to `sensors.name`.

**Architecture:** Two small query helpers and one presentation helper are added to `base/models.py` (domain layer) so the API serializer (`api/serializers.py`) and the web detail view (`sensors/views.py`) share the same account/sensor-name resolution instead of duplicating it. `api/views.py::PublicThingsViewSets` changes its queryset origin from the `accountsthings` join table to `Things` itself, so things without an account are no longer excluded.

**Tech Stack:** Django 3.2 + Django REST Framework. Tests use `django.test.SimpleTestCase` (no real database — the shared Postgres tables are `managed = False` with no test migrations) plus `unittest.mock.patch` to stub ORM managers, run via `python manage.py test`.

## Global Constraints

- Source code (variables, functions, classes, comments, log/error messages) in English; only `/docs` content is Portuguese — spec: `docs/superpowers/specs/2026-07-06-thing-visibility-sensor-name-design.md`.
- Never create or alter database schema from this repo — `thingssensors.name` (varchar(30) null) and `thingssensors.channel` (integer not null) already exist in the shared Postgres DB (owned by Sensoriando Core); only reflect them in `base/legacy_tables.py`.
- No new dependencies — no `pytest`. Use `django.test` (`django.test.SimpleTestCase`), executed via `python manage.py test`.
- Unit tests must not depend on real external services/DB — mock ORM managers with `unittest.mock.patch` (`docs/guidelines/testing.md`).
- TDD Red → Green → Refactor: write the failing test before the production code, every step.
- `PrivateThingsViewSets` is out of scope — it is already scoped to the logged-in user's own account and is unaffected.
- Functional use of the `channel` column is out of scope — map it on the model only.
- `thingssensors.name` is confirmed to always be `NULL` (never `""`) when not set — `Coalesce('name', 'id_sensor__name')` needs no extra empty-string handling.
- Fallback values when a thing has no account: city = `"não registrado"`, state = `""`, country = `"NR"` (literal, no `pycountry` conversion attempted).
- Never commit to `main`/`master`/`develop` directly; all work happens on `feat/thing-visibility-fallback` (already created off `develop`).

---

### Task 1: Map `thingssensors.name` and `thingssensors.channel` in the ORM

**Files:**
- Modify: `base/legacy_tables.py:138-148` (`Thingssensors` model)
- Test: `base/tests.py`

**Interfaces:**
- Produces: `Thingssensors.name` (`CharField(max_length=30, blank=True, null=True)`), `Thingssensors.channel` (`IntegerField()`) — consumed by Task 2's `get_thing_sensors_with_display_name`.

- [ ] **Step 1: Write the failing test**

Replace the contents of `base/tests.py` with:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test base.tests.ThingssensorsSchemaTests -v 2`
Expected: FAIL with `FieldDoesNotExist` (no field named 'name'/'channel' on Thingssensors).

- [ ] **Step 3: Write minimal implementation**

In `base/legacy_tables.py`, update the `Thingssensors` class:

```python
class Thingssensors(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')
    name = models.CharField(max_length=30, blank=True, null=True)
    channel = models.IntegerField()

    def __str__(self):
        return f"{self.id_thing} - {self.id_sensor}"

    class Meta:
        managed = False
        db_table = 'thingssensors'
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python manage.py test base.tests.ThingssensorsSchemaTests -v 2`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add base/legacy_tables.py base/tests.py
git commit -m "feat: map thingssensors.name and thingssensors.channel columns"
```

---

### Task 2: Add shared query helpers to `base/models.py`

**Files:**
- Modify: `base/models.py`
- Test: `base/tests.py`

**Interfaces:**
- Consumes: `ThingsSensorsModel` (`base/legacy_tables.py::Thingssensors` proxy, now with `.name`/`.channel` from Task 1), `AccountsModel`.
- Produces:
  - `get_thing_sensors_with_display_name(thing) -> QuerySet[ThingsSensorsModel]` — each row annotated with `.display_name` (`Coalesce('name', 'id_sensor__name')`). Consumed by Task 4 (`api/serializers.py`) and Task 6 (`sensors/views.py`).
  - `get_thing_account(thing) -> AccountsModel | None` — the account linked to `thing` (by id or instance) via `accountsthings`, or `None` if there is none. Consumed by Task 4 and Task 6.
  - `resolve_account_display(account) -> dict` — `{"is_public": bool, "city": str, "state": str, "country": str}`, with fallback `{"is_public": True, "city": "não registrado", "state": "", "country": "NR"}` when `account` is `None`. Consumed by Task 6.

- [ ] **Step 1: Write the failing tests**

Append to `base/tests.py`:

```python
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.db.models.functions import Coalesce

from base.models import (
    get_thing_account,
    get_thing_sensors_with_display_name,
    resolve_account_display,
)


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python manage.py test base.tests -v 2`
Expected: FAIL with `ImportError: cannot import name 'get_thing_sensors_with_display_name' from 'base.models'` (function doesn't exist yet).

- [ ] **Step 3: Write minimal implementation**

Add to `base/models.py`, after the model class definitions (keep existing content above untouched, add at the end of the file):

```python
from django.db.models.functions import Coalesce


def get_thing_sensors_with_display_name(thing):
    return ThingsSensorsModel.objects.filter(id_thing=thing).annotate(
        display_name=Coalesce('name', 'id_sensor__name')
    )


def get_thing_account(thing):
    return AccountsModel.objects.filter(
        accountsthings__id_thing=thing
    ).select_related('id_plan').first()


def resolve_account_display(account):
    if not account:
        return {
            "is_public": True,
            "city": "não registrado",
            "state": "",
            "country": "NR",
        }

    return {
        "is_public": account.id_plan.ispublic,
        "city": account.city,
        "state": account.state,
        "country": account.country,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test base.tests -v 2`
Expected: PASS (6 tests total: 2 from Task 1 + 4 new).

- [ ] **Step 5: Commit**

```bash
git add base/models.py base/tests.py
git commit -m "feat: add shared thing/account/sensor-name query helpers"
```

---

### Task 3: Include things without an account in the public listing

**Files:**
- Modify: `api/views.py:101-105` (`PublicThingsViewSets.get_queryset`)
- Test: `api/tests.py`

**Interfaces:**
- Consumes: `ThingsModel` (already imported in `api/views.py`), `Q` (already imported).
- Produces: `PublicThingsViewSets.get_queryset(params)` now returns a `QuerySet[ThingsModel]` (previously `QuerySet[AccountsThingsModel]`) — Task 4's serializer must be adapted to receive `ThingsModel` instances.

- [ ] **Step 1: Write the failing test**

Replace the contents of `api/tests.py` with:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test api.tests.PublicThingsGetQuerysetTests -v 2`
Expected: FAIL — actual call args to `mock_objects.filter` don't match `expected_q` (current implementation still filters on `id_account__status`/`id_account__id_plan__ispublic` directly, with no `accountsthings__` prefix, and doesn't call `.distinct()`).

- [ ] **Step 3: Write minimal implementation**

In `api/views.py`, replace `PublicThingsViewSets.get_queryset`:

```python
def get_queryset(self, params):
    return ThingsModel.objects.filter(
        Q(accountsthings__isnull = True) |
        Q(accountsthings__id_account__status = True,
          accountsthings__id_account__id_plan__ispublic = True)
    ).distinct()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python manage.py test api.tests.PublicThingsGetQuerysetTests -v 2`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api/views.py api/tests.py
git commit -m "feat: include things without an account in the public listing"
```

---

### Task 4: Adapt `DataThingsSerializer` to `Things` instances with account/sensor fallback

**Files:**
- Modify: `api/serializers.py:6-7` (imports), `api/serializers.py:48-86` (`DataThingsSerializer`)
- Test: `api/tests.py`

**Interfaces:**
- Consumes: `get_thing_sensors_with_display_name(thing)`, `get_thing_account(thing)` (from Task 2, `base.models`), `ThingsModel` (Task 3 now feeds `DataThingsSerializer` instances of this type).
- Produces: `DataThingsSerializer.get_account(obj)` returns `{"username": str|None, "city": str, "state": str, "country": str}` (fallback dict when no account). `DataThingsSerializer.get_sensors(obj)` returns `[{"id": int, "name": str}, ...]` using the resolved display name.

- [ ] **Step 1: Write the failing tests**

Append to `api/tests.py`:

```python
from types import SimpleNamespace

from api.serializers import DataThingsSerializer


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python manage.py test api.tests -v 2`
Expected: FAIL — `get_thing_account`/`get_thing_sensors_with_display_name` are not imported/used yet in `api/serializers.py`, and `get_thing`/`get_uuid`/`get_sensors` still read `obj.id_thing.*`, so calling with a plain `SimpleNamespace` thing raises `AttributeError`.

- [ ] **Step 3: Write minimal implementation**

In `api/serializers.py`, update the import block (lines 6-7):

```python
from base.models import ThingsModel, ThingsTagsModel, SensorsModel, ThingsSensorsTagsModel, \
                        AccountsModel, AccountsThingsModel, ThingsSensorsModel, ThingsSensorsDataModel, \
                        get_thing_sensors_with_display_name, get_thing_account
```

Replace `DataThingsSerializer` (lines 48-86):

```python
class DataThingsSerializer(serializers.ModelSerializer):
    thing = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()
    account = serializers.SerializerMethodField()
    sensors = serializers.SerializerMethodField()
    lastupdate = serializers.SerializerMethodField()
    thingtags = serializers.SerializerMethodField()

    class Meta:
        model = ThingsModel
        fields = ('thing', 'uuid', 'lastupdate', 'account', 'sensors', 'thingtags')

    def get_thing(self, obj):
        return obj.name

    def get_uuid(self, obj):
        return obj.uuid

    def get_account(self, obj):
        account = get_thing_account(obj)

        if not account:
            return {
                "username": None,
                "city": "não registrado",
                "state": "",
                "country": "NR",
            }

        return AccountSerializer(account).data

    def get_sensors(self, obj):
        thing_sensors = get_thing_sensors_with_display_name(obj)
        return [
            {"id": ts.id_sensor_id, "name": ts.display_name}
            for ts in thing_sensors
        ]

    def get_thingtags(self, obj):
        thing_tags = ThingsTagsModel.objects.filter(id_thing = obj)
        return SensorSerializer(thing_tags, many = True).data

    def get_lastupdate(self, obj):
        thingsensor_ids = ThingsSensorsModel.objects.filter(id_thing = obj)
        lastread = ThingsSensorsDataModel.objects.filter(id_thingsensor__in = thingsensor_ids).aggregate(Max('dtread'))['dtread__max']

        return lastread.strftime("%d/%m/%Y %H:%M:%S") if lastread else "---"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test api.tests -v 2`
Expected: PASS (all `api.tests` cases, including Task 3's).

- [ ] **Step 5: Commit**

```bash
git add api/serializers.py api/tests.py
git commit -m "feat: resolve thing account and sensor display name with fallbacks"
```

---

### Task 5: Make `overview/views.py::getCountry` tolerant of missing accounts

**Files:**
- Modify: `overview/views.py:36-44` (`getCountry`)
- Test: `overview/tests.py`

**Interfaces:**
- Consumes: nothing new (still plain dicts from the `/things/` API response).
- Produces: `getCountry(jsonResult)` no longer raises when an item's `"account"` is `None`/missing, and leaves the literal `"NR"` untouched instead of trying to convert it via `pycountry`.

- [ ] **Step 1: Write the failing tests**

Replace the contents of `overview/tests.py` with:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python manage.py test overview.tests -v 2`
Expected: FAIL on `test_skips_items_without_account` with `TypeError: argument of type 'NoneType' is not iterable` (current `"country" in item["account"]` crashes when `account` is `None`).

- [ ] **Step 3: Write minimal implementation**

In `overview/views.py`, replace `getCountry`:

```python
def getCountry(jsonResult):
    if jsonResult:
        for item in jsonResult:
            account = item.get("account")

            if not account:
                continue

            country_code = account.get("country")

            if not country_code or country_code == "NR":
                continue

            country = pycountry.countries.get(alpha_2=country_code)

            if country:
                account["country"] = country.name

    return jsonResult
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py test overview.tests -v 2`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add overview/views.py overview/tests.py
git commit -m "fix: handle things without an account in getCountry"
```

---

### Task 6: Fix the thing detail page for things without an account

**Files:**
- Modify: `sensors/views.py:1-11` (imports), `sensors/views.py:33-92` (`ThingDetails`)
- Test: `sensors/tests.py`

**Interfaces:**
- Consumes: `get_thing_account(thing)`, `get_thing_sensors_with_display_name(thing)`, `resolve_account_display(account)` (Task 2, `base.models`).
- Produces: `ThingDetails` no longer raises `DoesNotExist` (500) for a thing with no account; template context always has `city`/`state`/`country` populated (with fallback), and the public/private data endpoint choice defaults to public when there is no account.

- [ ] **Step 1: Write the failing test**

This task's new business logic (fallback resolution) is already covered by `ResolveAccountDisplayTests` in Task 2 — `ThingDetails` itself is a heavy view (cookies, `callAPI`, pandas) with no existing test harness, so this task adds one focused regression test instead of a full view test: that the view no longer calls `AccountsModel.objects.get` (which raises `DoesNotExist` for an accountless thing).

Replace the contents of `sensors/tests.py` with:

```python
import inspect

from django.test import SimpleTestCase

from sensors import views


class ThingDetailsAccountLookupTests(SimpleTestCase):
    def test_does_not_use_unsafe_get_lookup_for_account(self):
        source = inspect.getsource(views.ThingDetails)

        self.assertNotIn("AccountsModel.objects.get(", source)
        self.assertIn("get_thing_account(", source)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python manage.py test sensors.tests -v 2`
Expected: FAIL — `ThingDetails` still calls `AccountsModel.objects.get(accountsthings__id_thing = thing.id)`.

- [ ] **Step 3: Write minimal implementation**

In `sensors/views.py`, update the import block (lines 1-11):

```python
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse

from base.views import callAPI
from users.views import check_and_refresh_token
from base.models import (
    ThingsModel,
    AccountsModel,
    PlansModel,
    ThingsSensorsModel,
    ThingsTagsModel,
    SensorsUnitsModel,
    get_thing_account,
    get_thing_sensors_with_display_name,
    resolve_account_display,
)

from dateutil.parser import parse
import pandas as pd
import json
```

Then, inside `ThingDetails`, replace the data-loading block (originally lines 33-36):

```python
    thing = ThingsModel.objects.get(uuid = uuid)
    thingtags = ThingsTagsModel.objects.filter(id_thing = thing.id)
    thingssensors = get_thing_sensors_with_display_name(thing.id)
    account = get_thing_account(thing.id)
    account_display = resolve_account_display(account)
```

Replace the sensor-name line (originally line 45):

```python
        sensor = thingsensor.display_name
```

Replace the public/private branch (originally lines 92-104):

```python
        if account_display["is_public"]:
            jsonResult = callAPI(
                endpoint = "/data/detail/", \
                data = jsonParams, \
                method = "POST"
            )
        else:
            jsonResult = callAPI(
                endpoint = "/data/detail/private/", \
                data = jsonParams, \
                method = "POST", \
                token = check_and_refresh_token()
            )
```

Replace the context block (originally lines 139-149):

```python
    context = {
        'thing': thing.name,
        'thing_tags': tags,
        'chart_file': 'chart.js',
        'city': account_display["city"],
        'state': account_display["state"],
        'title': chartView,
        'country': account_display["country"],
        'sensors': sensors,

    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python manage.py test sensors.tests -v 2`
Expected: PASS.

- [ ] **Step 5: Run the full test suite**

Run: `python manage.py test base api overview sensors -v 2`
Expected: PASS — all tests from Tasks 1-6 (17 tests total: 2 + 4 + 1 + 5 + 4 + 1).

- [ ] **Step 6: Commit**

```bash
git add sensors/views.py sensors/tests.py
git commit -m "fix: stop 500ing on thing detail page when there is no account"
```

- [ ] **Step 7: Manual verification**

Since `ThingDetails` has no automated end-to-end coverage (no test DB for the `managed = False` tables, no existing request/response fixtures for `callAPI`), confirm behavior by hand once a real accountless thing exists in a dev database:

1. Start the stack (see `run.sh`).
2. Open `/thing/detail/<uuid>` for a `Thing` with no row in `accountsthings`.
3. Confirm the page renders (no 500), city/state/country show the fallback values, and the sensor names shown match `thingssensors.name` when set, or the catalog `sensors.name` otherwise.
4. Open `/` (public listing) and confirm the same thing now appears in the list.
