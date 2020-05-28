# Generated by Django 3.0.5 on 2020-05-27 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('username', models.CharField(max_length=20, unique=True)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=2)),
                ('country', models.CharField(max_length=2)),
                ('ispublic', models.BooleanField()),
                ('status', models.BooleanField()),
                ('usetrigger', models.BooleanField()),
            ],
            options={
                'db_table': 'accounts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Accountsthings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
            ],
            options={
                'db_table': 'accountsthings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sensors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'db_table': 'sensors',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sensorsparams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('key', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'sensorsparams',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sensorsunits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('name', models.CharField(max_length=50, unique=True)),
                ('initial', models.CharField(blank=True, max_length=5, null=True)),
                ('precision', models.SmallIntegerField(blank=True, null=True)),
                ('isdefault', models.BooleanField()),
                ('expression', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'sensorsunits',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Things',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('name', models.CharField(max_length=30)),
                ('uuid', models.UUIDField(unique=True)),
                ('isrelay', models.BooleanField()),
            ],
            options={
                'db_table': 'things',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Thingsdata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('qos', models.IntegerField()),
                ('retained', models.BooleanField()),
                ('payload', models.TextField()),
            ],
            options={
                'db_table': 'thingsdata',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Thingsflags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'thingsflags',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Thingsparams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt', models.DateTimeField()),
                ('key', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'thingsparams',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Vwaccountsthings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_account', models.IntegerField(blank=True, null=True)),
                ('dt_account', models.DateTimeField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(blank=True, max_length=2, null=True)),
                ('country', models.CharField(blank=True, max_length=20, null=True)),
                ('usetrigger', models.BooleanField(blank=True, null=True)),
                ('ispublic', models.BooleanField(blank=True, null=True)),
                ('id_thing', models.IntegerField(blank=True, null=True)),
                ('dt_thing', models.DateTimeField(blank=True, null=True)),
                ('thing', models.CharField(blank=True, max_length=30, null=True)),
                ('uuid', models.UUIDField(blank=True, null=True)),
                ('isrelay', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'vwaccountsthings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Vwaccountsthingssensorsunits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_account', models.IntegerField(blank=True, null=True)),
                ('id_thing', models.IntegerField(blank=True, null=True)),
                ('id_sensor', models.IntegerField(blank=True, null=True)),
                ('id_unit', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'vwaccountsthingssensorsunits',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Vwthingsdata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_thingdatum', models.IntegerField(blank=True, null=True)),
                ('dt_thingdatum', models.DateTimeField(blank=True, null=True)),
                ('id_thing', models.IntegerField(blank=True, null=True)),
                ('id_sensor', models.IntegerField(blank=True, null=True)),
                ('qos', models.IntegerField(blank=True, null=True)),
                ('retained', models.BooleanField(blank=True, null=True)),
                ('payload_dt', models.DateTimeField(blank=True, null=True)),
                ('payload_value', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'vwthingsdata',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
            ],
            options={
                'verbose_name': 'Account',
                'verbose_name_plural': 'Accounts',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('base.accounts',),
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
            ],
            options={
                'verbose_name': 'Sensor',
                'verbose_name_plural': 'Sensors',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('base.sensors',),
        ),
        migrations.CreateModel(
            name='Thing',
            fields=[
            ],
            options={
                'verbose_name': 'Thing',
                'verbose_name_plural': 'Things',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('base.things',),
        ),
    ]
