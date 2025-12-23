from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
from .models import Company, Customer, Invoice, InvoiceItem, ZATCALog
from .forms import CompanyForm, CustomerForm, InvoiceForm, InvoiceItemFormSet
from .zatca_service import ZATCAService


def home(view):
    """Home page with dashboard"""
    context = {
        'total_invoices': Invoice.objects.count(),
        'draft_invoices': Invoice.objects.filter(status='draft').count(),
        'submitted_invoices': Invoice.objects.filter(status='submitted').count(),
        'approved_invoices': Invoice.objects.filter(status='approved').count(),
        'recent_invoices': Invoice.objects.all()[:5],
    }
    return render(view, 'invoices/home.html', context)


# Company Views
def company_list(request):
    """List all companies"""
    companies = Company.objects.all()
    return render(request, 'invoices/company_list.html', {'companies': companies})


def company_create(request):
    """Create a new company"""
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company created successfully!')
            return redirect('company_list')
    else:
        form = CompanyForm()
    return render(request, 'invoices/company_form.html', {'form': form, 'action': 'Create'})


def company_edit(request, pk):
    """Edit a company"""
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company updated successfully!')
            return redirect('company_list')
    else:
        form = CompanyForm(instance=company)
    return render(request, 'invoices/company_form.html', {'form': form, 'action': 'Edit'})


def company_delete(request, pk):
    """Delete a company"""
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.delete()
        messages.success(request, 'Company deleted successfully!')
        return redirect('company_list')
    return render(request, 'invoices/company_confirm_delete.html', {'company': company})


# Customer Views
def customer_list(request):
    """List all customers"""
    customers = Customer.objects.all()
    return render(request, 'invoices/customer_list.html', {'customers': customers})


def customer_create(request):
    """Create a new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'invoices/customer_form.html', {'form': form, 'action': 'Create'})


def customer_edit(request, pk):
    """Edit a customer"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'invoices/customer_form.html', {'form': form, 'action': 'Edit'})


def customer_delete(request, pk):
    """Delete a customer"""
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')
    return render(request, 'invoices/customer_confirm_delete.html', {'customer': customer})


# Invoice Views
def invoice_list(request):
    """List all invoices"""
    invoices = Invoice.objects.all()
    status_filter = request.GET.get('status')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


def invoice_detail(request, pk):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, pk=pk)
    logs = invoice.zatca_logs.all()
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice, 'logs': logs})


def invoice_create(request):
    """Create a new invoice"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            if request.user.is_authenticated:
                invoice.created_by = request.user
            invoice.save()
            
            formset.instance = invoice
            formset.save()
            
            # Calculate totals
            invoice.calculate_totals()
            
            messages.success(request, 'Invoice created successfully!')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(initial={
            'issue_date': datetime.now().date(),
            'issue_time': datetime.now().time()
        })
        formset = InvoiceItemFormSet()
    
    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
        'action': 'Create'
    })


def invoice_edit(request, pk):
    """Edit an invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Can only edit draft invoices
    if invoice.status != 'draft':
        messages.error(request, 'Can only edit draft invoices!')
        return redirect('invoice_detail', pk=pk)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            invoice.calculate_totals()
            
            messages.success(request, 'Invoice updated successfully!')
            return redirect('invoice_detail', pk=invoice.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    
    return render(request, 'invoices/invoice_form.html', {
        'form': form,
        'formset': formset,
        'action': 'Edit',
        'invoice': invoice
    })


def invoice_delete(request, pk):
    """Delete an invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # Can only delete draft invoices
    if invoice.status != 'draft':
        messages.error(request, 'Can only delete draft invoices!')
        return redirect('invoice_detail', pk=pk)
    
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully!')
        return redirect('invoice_list')
    
    return render(request, 'invoices/invoice_confirm_delete.html', {'invoice': invoice})


def invoice_submit_zatca(request, pk):
    """Submit invoice to ZATCA"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.status != 'draft':
        messages.error(request, 'Invoice already submitted or not in draft status!')
        return redirect('invoice_detail', pk=pk)
    
    if request.method == 'POST':
        zatca_service = ZATCAService()
        success, message, data = zatca_service.submit_invoice(invoice)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect('invoice_detail', pk=pk)
    
    return render(request, 'invoices/invoice_submit_confirm.html', {'invoice': invoice})


def invoice_check_status(request, pk):
    """Check invoice status from ZATCA"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    zatca_service = ZATCAService()
    success, message, data = zatca_service.check_invoice_status(invoice)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': message,
            'data': data
        })
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('invoice_detail', pk=pk)


def invoice_cancel(request, pk):
    """Cancel an invoice in ZATCA"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.status not in ['submitted', 'approved']:
        messages.error(request, 'Can only cancel submitted or approved invoices!')
        return redirect('invoice_detail', pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Cancelled by user')
        zatca_service = ZATCAService()
        success, message, data = zatca_service.cancel_invoice(invoice, reason)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect('invoice_detail', pk=pk)
    
    return render(request, 'invoices/invoice_cancel_confirm.html', {'invoice': invoice})


def invoice_print(request, pk):
    """Print invoice"""
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoices/invoice_print.html', {'invoice': invoice})
