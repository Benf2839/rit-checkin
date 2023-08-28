from django.contrib import admin

from . import models

admin.site.register(models.LogMessage)
admin.site.register(models.db_model)
admin.site.register(models.import_csv)
admin.site.register(models.RIT)
admin.site.register(models.Company_2)
