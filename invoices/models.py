from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    """Company/Seller Information"""
    name = models.CharField(max_length=255)
    vat_number = models.CharField(max_length=15, unique=True)
    cr_number = models.CharField(max_length=20, verbose_name="Commercial Registration Number")
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=2, default='SA')
    building_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=255)
    district = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Customer/Buyer Information"""
    name = models.CharField(max_length=255)
    vat_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=2, default='SA')
    building_number = models.CharField(max_length=10, blank=True, null=True)
    street_name = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    """E-Invoice for ZATCA"""
    INVOICE_TYPES = [
        ('standard', 'Standard Invoice'),
        ('simplified', 'Simplified Invoice'),
        ('debit', 'Debit Note'),
        ('credit', 'Credit Note'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted to ZATCA'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    # Invoice Basic Info
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPES, default='standard')
    issue_date = models.DateField()
    issue_time = models.TimeField()
    
    # Company and Customer
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    
    # Financial Details
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # ZATCA Specific Fields
    uuid = models.CharField(max_length=255, blank=True, null=True, verbose_name="ZATCA UUID")
    qr_code = models.TextField(blank=True, null=True)
    zatca_response = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Additional Info
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-issue_time']

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"

    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        items = self.items.all()
        self.subtotal = sum(item.total for item in items)
        self.vat_amount = sum(item.vat_amount for item in items)
        self.total = self.subtotal + self.vat_amount - self.discount
        self.save()


class InvoiceItem(models.Model):
    """Invoice Line Items"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        """Calculate line item totals"""
        line_total = self.quantity * self.unit_price - self.discount
        self.vat_amount = line_total * (self.vat_rate / 100)
        self.total = line_total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"


class ZATCALog(models.Model):
    """Log ZATCA API interactions"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='zatca_logs')
    action = models.CharField(max_length=50)
    request_data = models.JSONField()
    response_data = models.JSONField(blank=True, null=True)
    status_code = models.IntegerField(blank=True, null=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.invoice.invoice_number} - {self.timestamp}"
