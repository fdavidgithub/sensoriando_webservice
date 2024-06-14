from django.contrib import admin
from base.models import AccountsModel, ThingsModel, SensorsModel, PlansModel, SensorsUnitsModel, ThingsTagsModel, ThingsSensorsTagsModel, \
                        AccountsThingsModel, ThingsSensorsModel

# Register your models here.
admin.site.register(AccountsModel)
admin.site.register(ThingsModel)
admin.site.register(SensorsModel)
admin.site.register(PlansModel)
admin.site.register(SensorsUnitsModel)
admin.site.register(ThingsTagsModel)
admin.site.register(ThingsSensorsTagsModel)
admin.site.register(AccountsThingsModel)
admin.site.register(ThingsSensorsModel)
