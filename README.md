# ZATCA E-Invoice System

A complete Django web application for managing electronic invoices integrated with the ZATCA (Zakat, Tax and Customs Authority) API in Saudi Arabia.

## Features

### Core Functionality
- **Invoice Management**: Create, edit, view, and delete invoices
- **Company Management**: Manage seller information (VAT number, CR number, address)
- **Customer Management**: Manage buyer information and contact details
- **ZATCA Integration**: Submit invoices to ZATCA, check status, and cancel invoices
- **QR Code Generation**: Automatic QR code generation for simplified invoices
- **Multiple Invoice Types**: Support for standard invoices, simplified invoices, debit notes, and credit notes
- **VAT Calculation**: Automatic VAT calculation on line items
- **Invoice Status Tracking**: Draft, Submitted, Approved, Rejected, Cancelled

### User Interface
- **Responsive Design**: Bootstrap 5-based UI that works on desktop and mobile
- **Dashboard**: Overview of invoices with quick stats
- **Print View**: Professional invoice print layout with Arabic/English support
- **Activity Logs**: Track all ZATCA API interactions

## Project Structure

```
zatca_full/
├── invoices/                # Main app
│   ├── models.py           # Database models (Company, Customer, Invoice, etc.)
│   ├── views.py            # View functions for all pages
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin panel configuration
│   ├── zatca_service.py    # ZATCA API integration service
│   └── templates/          # HTML templates
│       └── invoices/       
│           ├── base.html            # Base template
│           ├── home.html            # Dashboard
│           ├── invoice_*.html       # Invoice templates
│           ├── company_*.html       # Company templates
│           └── customer_*.html      # Customer templates
├── static/                 # Static files
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── main.js         # JavaScript functionality
├── zatca_project/          # Django project settings
│   ├── settings.py         # Project settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── manage.py               # Django management script
└── db.sqlite3              # SQLite database (created after migration)
```

## Installation & Setup

### 1. Prerequisites
- Python 3.8+ installed
- Virtual environment activated 
- Django installed

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin User
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### 5. Run the Development Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to access the application.

## Configuration

### ZATCA API Settings
Edit `zatca_project/settings.py` to configure ZATCA API:

```python
# ZATCA API Configuration
ZATCA_API_URL = 'https://api.zatca.gov.sa/e-invoicing'  # Update with actual endpoint
ZATCA_API_KEY = 'your-api-key-here'  # Add your ZATCA API key
ZATCA_CERTIFICATE_PATH = BASE_DIR / 'certificates'
```

**Note**: The current implementation includes a mock ZATCA service. You'll need to update the `zatca_service.py` file with actual ZATCA API endpoints and authentication methods based on ZATCA's official documentation.

## Usage

### 1. Access the Application
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### 2. Initial Setup
1. Log in to the admin panel
2. Create at least one Company (your business information)
3. Add Customers

### 3. Creating Invoices
1. From the dashboard, click "Create New Invoice"
2. Fill in invoice details:
   - Invoice number (must be unique)
   - Select company and customer
   - Choose invoice type
   - Set date and time
3. Add line items with description, quantity, price, and VAT rate
4. Save the invoice (status: Draft)

### 4. Submitting to ZATCA
1. Open the invoice detail page
2. Click "Submit to ZATCA"
3. The system will send the invoice data to ZATCA API
4. Status will update based on ZATCA response
5. QR code will be generated for approved invoices

### 5. Managing Invoices
- **Edit**: Only draft invoices can be edited
- **Delete**: Only draft invoices can be deleted
- **Cancel**: Submitted/approved invoices can be cancelled through ZATCA
- **Print**: All invoices can be printed with bilingual (Arabic/English) format

## Models

### Company
- Company information (seller)
- VAT number, CR number
- Address details

### Customer
- Customer information (buyer)
- Optional VAT number
- Contact information

### Invoice
- Invoice header information
- Links to Company and Customer
- Financial totals
- ZATCA status and response data

### InvoiceItem
- Line items for invoices
- Automatic VAT calculation
- Discount support

### ZATCALog
- Tracks all ZATCA API interactions
- Stores request/response data
- Error logging

## API Integration

The `zatca_service.py` module provides:
- `submit_invoice()`: Submit invoice to ZATCA
- `check_invoice_status()`: Query invoice status
- `cancel_invoice()`: Cancel an invoice
- `generate_qr_code()`: Generate QR code in TLV format

## Security Notes

1. **SECRET_KEY**: Change the Django secret key in production
2. **DEBUG**: Set `DEBUG = False` in production
3. **ALLOWED_HOSTS**: Configure allowed hosts for production
4. **API Keys**: Store ZATCA API credentials securely (environment variables)
5. **HTTPS**: Use HTTPS in production
6. **Database**: Use PostgreSQL or MySQL in production instead of SQLite

## Next Steps

### For Production:
1. Update ZATCA API endpoints with actual URLs
2. Implement proper authentication with ZATCA
3. Add certificate management for ZATCA integration
4. Set up proper logging and monitoring
5. Configure production database
6. Enable user authentication and permissions
7. Add data validation and error handling
8. Implement backup procedures

### Optional Enhancements:
- PDF generation for invoices
- Email notifications
- Multi-language support
- Advanced reporting and analytics
- Export to Excel/CSV
- Bulk invoice operations
- Invoice templates
- Payment tracking

## Troubleshooting

### Database Issues
```bash
# Reset database
python manage.py flush
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [ZATCA E-Invoicing Portal](https://zatca.gov.sa/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)

## License

This project is for educational and development purposes.

## Support

For issues and questions, please refer to ZATCA's official e-invoicing documentation and guidelines.
