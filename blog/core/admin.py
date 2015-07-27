from django.contrib import admin

from blog.core import models


admin.site.register(models.Post)
admin.site.register(models.Blog)
