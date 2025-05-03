from django.contrib import admin

from manager_app import models

admin.site.register(models.Chat)
admin.site.register(models.Employee)
admin.site.register(models.EmployeeAccount)
admin.site.register(models.ModelResponseStrategy)
admin.site.register(models.GenerationSettings)