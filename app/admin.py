from django.contrib import admin
from . import models
admin.site.register(models.Activity)
admin.site.register(models.Kudos)
admin.site.register(models.Comment)