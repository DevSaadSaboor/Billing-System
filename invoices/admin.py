from django.contrib import admin
from .models import Invoice,InvoiceLineItem


class InvoiceLineItemAdmin(admin.ModelAdmin):
    readonly_fields = ['line_subtotal', 'line_tax', 'line_total']


admin.site.register(Invoice)
admin.site.register(InvoiceLineItem,InvoiceLineItemAdmin)