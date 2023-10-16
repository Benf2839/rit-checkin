from django.contrib import admin

from . import models

admin.site.register(models.db_model)
admin.site.register(models.EmailConfiguration)
