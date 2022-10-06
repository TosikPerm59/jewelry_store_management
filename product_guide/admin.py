from django.contrib import admin
from django.contrib.messages.storage import session

from .models import Jewelry, Metal, InputInvoice, OutgoingInvoice, Provider, Recipient, File


class JewelryAdmin(admin.ModelAdmin):
    list_display = ('name', 'metal', 'weight')


admin.site.register(Jewelry, JewelryAdmin)
admin.site.register(Metal)
admin.site.register(InputInvoice)
admin.site.register(OutgoingInvoice)
admin.site.register(Provider)
admin.site.register(Recipient)
admin.site.register(File)

