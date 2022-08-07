from django.contrib import admin
from .models import Jewelry


class ProductGuide(admin.ModelAdmin):
    list_display = ('name', 'metal', 'weight')


admin.site.register(Jewelry)
