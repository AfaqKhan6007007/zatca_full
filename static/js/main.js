// Main JavaScript for ZATCA E-Invoice System

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirmation dialogs for dangerous actions
    const dangerousForms = document.querySelectorAll('form[action*="delete"], form[action*="cancel"]');
    dangerousForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const action = this.action.includes('delete') ? 'delete' : 'cancel';
            if (!confirm(`Are you sure you want to ${action} this item?`)) {
                e.preventDefault();
            }
        });
    });

    // Invoice form calculations
    const invoiceForm = document.getElementById('invoice-form');
    if (invoiceForm) {
        setupInvoiceCalculations();
    }

    // Table row highlight
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            const link = this.querySelector('a[href]');
            if (link && !event.target.closest('a, button')) {
                window.location.href = link.href;
            }
        });
    });
});

// Invoice calculations
function setupInvoiceCalculations() {
    const itemsContainer = document.getElementById('invoice-items');
    if (!itemsContainer) return;

    // Delegate event listeners for dynamic forms
    itemsContainer.addEventListener('input', function(e) {
        const input = e.target;
        if (input.matches('input[type="number"]')) {
            const formRow = input.closest('.formset-row');
            if (formRow) {
                calculateRowTotal(formRow);
            }
        }
    });
}

function calculateRowTotal(row) {
    const quantityInput = row.querySelector('input[name$="-quantity"]');
    const priceInput = row.querySelector('input[name$="-unit_price"]');
    const vatRateInput = row.querySelector('input[name$="-vat_rate"]');
    const discountInput = row.querySelector('input[name$="-discount"]');

    if (!quantityInput || !priceInput || !vatRateInput) return;

    const quantity = parseFloat(quantityInput.value) || 0;
    const price = parseFloat(priceInput.value) || 0;
    const vatRate = parseFloat(vatRateInput.value) || 0;
    const discount = parseFloat(discountInput?.value) || 0;

    const subtotal = (quantity * price) - discount;
    const vatAmount = subtotal * (vatRate / 100);
    const total = subtotal + vatAmount;

    // You could display these calculated values if you had display fields
    console.log('Row calculations:', {
        subtotal: subtotal.toFixed(2),
        vatAmount: vatAmount.toFixed(2),
        total: total.toFixed(2)
    });
}

// AJAX status check
function checkInvoiceStatus(invoiceId) {
    fetch(`/invoices/${invoiceId}/status/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Status updated successfully', 'success');
            location.reload();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        showNotification('Error checking status', 'error');
        console.error('Error:', error);
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';

    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Print invoice
function printInvoice(invoiceId) {
    window.open(`/invoices/${invoiceId}/print/`, '_blank');
}

// Export functionality (placeholder for future implementation)
function exportToExcel() {
    console.log('Export to Excel functionality to be implemented');
    showNotification('Export feature coming soon!', 'info');
}

function exportToPDF() {
    console.log('Export to PDF functionality to be implemented');
    showNotification('Export feature coming soon!', 'info');
}
