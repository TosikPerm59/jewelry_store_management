from django.contrib import admin
from django.contrib.messages.storage import session

from .models import *


class JewelryAdmin(admin.ModelAdmin):
    list_display = ('name', 'metal', 'weight')
    list_display_links = ('name', 'metal')


class OutgoingInvoiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient')


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('title', 'inn')


admin.site.register(Jewelry, JewelryAdmin)
admin.site.register(Metal)
admin.site.register(InputInvoice)
admin.site.register(OutgoingInvoice, OutgoingInvoiceAdmin)
admin.site.register(Provider)
admin.site.register(Recipient)
admin.site.register(File)
admin.site.register(Counterparties)
admin.site.register(Manufacturer, ManufacturerAdmin)

