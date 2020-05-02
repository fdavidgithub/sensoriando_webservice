# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Accounts(models.Model):
    dt = models.DateTimeField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=20)
    ispublic = models.BooleanField()
    status = models.BooleanField()
    usetrigger = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'accounts'


class Accountsthings(models.Model):
    dt = models.DateTimeField()
    id_account = models.ForeignKey(Accounts, models.DO_NOTHING, db_column='id_account')
    id_thing = models.ForeignKey('Things', models.DO_NOTHING, db_column='id_thing')

    class Meta:
        managed = False
        db_table = 'accountsthings'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Sensors(models.Model):
    dt = models.DateTimeField()
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'sensors'


class Sensorsparams(models.Model):
    dt = models.DateTimeField()
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=10)
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')

    class Meta:
        managed = False
        db_table = 'sensorsparams'
        unique_together = (('id_sensor', 'key'),)


class Sensorsunits(models.Model):
    dt = models.DateTimeField()
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')
    name = models.CharField(unique=True, max_length=50)
    initial = models.CharField(max_length=5, blank=True, null=True)
    precision = models.SmallIntegerField(blank=True, null=True)
    isdefault = models.BooleanField()
    expression = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensorsunits'
        unique_together = (('id_sensor', 'name'),)


class Things(models.Model):
    dt = models.DateTimeField()
    name = models.CharField(max_length=30)
    uuid = models.UUIDField(unique=True)
    isrelay = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'things'


class Thingsdata(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    id_sensor = models.ForeignKey(Sensors, models.DO_NOTHING, db_column='id_sensor')
    qos = models.IntegerField()
    retained = models.BooleanField()
    payload = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'thingsdata'
        unique_together = (('id_thing', 'id_sensor', 'payload'),)


class Thingsflags(models.Model):
    dt = models.DateTimeField()
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')
    name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'thingsflags'
        unique_together = (('id_thing', 'name'),)


class Thingsparams(models.Model):
    dt = models.DateTimeField()
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=10)
    id_thing = models.ForeignKey(Things, models.DO_NOTHING, db_column='id_thing')

    class Meta:
        managed = False
        db_table = 'thingsparams'
        unique_together = (('id_thing', 'key'),)


class Vwaccountsthings(models.Model):
    id_account = models.IntegerField(primary_key=True)
    dt_account = models.DateTimeField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    usetrigger = models.BooleanField(blank=True, null=True)
    ispublic = models.BooleanField(blank=True, null=True)
    id_thing = models.IntegerField(blank=True, null=True)
    dt_thing = models.DateTimeField(blank=True, null=True)
    thing = models.CharField(max_length=30, blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)
    isrelay = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'vwaccountsthings'


class Vwthingsdata(models.Model):
    id = models.IntegerField(primary_key=True)
    dt = models.DateTimeField(blank=True, null=True)
    id_thing = models.IntegerField(blank=True, null=True)
    id_sensor = models.IntegerField(blank=True, null=True)
    qos = models.IntegerField(blank=True, null=True)
    retained = models.BooleanField(blank=True, null=True)
    payload_dt = models.DateTimeField(blank=True, null=True)
    payload_value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = 'vwthingsdata'
