from django.contrib import admin
from .models import Company, Customer, Invoice, InvoiceItem, ZATCALog


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'vat_number', 'cr_number', 'city', 'created_at']
    search_fields = ['name', 'vat_number', 'cr_number']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'vat_number', 'city', 'email', 'phone', 'created_at']
    search_fields = ['name', 'vat_number', 'email']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'invoice_type', 'issue_date', 'total', 'status', 'created_at']
    list_filter = ['status', 'invoice_type', 'issue_date']
    search_fields = ['invoice_number', 'customer__name']
    inlines = [InvoiceItemInline]
    readonly_fields = ['uuid', 'qr_code', 'zatca_response', 'created_at', 'updated_at']


@admin.register(ZATCALog)
class ZATCALogAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'action', 'success', 'status_code', 'timestamp']
    list_filter = ['success', 'action', 'timestamp']
    search_fields = ['invoice__invoice_number']
    readonly_fields = ['invoice', 'action', 'request_data', 'response_data', 'status_code', 'success', 'error_message', 'timestamp']
