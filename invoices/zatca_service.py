import requests
import json
import base64
from datetime import datetime
from django.conf import settings
from .models import ZATCALog


class ZATCAService:
    """Service class to handle ZATCA API integration"""
    
    def __init__(self):
        self.api_url = settings.ZATCA_API_URL
        self.api_key = settings.ZATCA_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def prepare_invoice_data(self, invoice):
        """
        Prepare invoice data in ZATCA format
        This is a sample structure - adjust based on actual ZATCA API requirements
        """
        invoice_data = {
            "invoiceNumber": invoice.invoice_number,
            "invoiceType": invoice.invoice_type,
            "issueDate": invoice.issue_date.isoformat(),
            "issueTime": invoice.issue_time.isoformat(),
            "seller": {
                "name": invoice.company.name,
                "vatNumber": invoice.company.vat_number,
                "crNumber": invoice.company.cr_number,
                "address": {
                    "street": invoice.company.street_name,
                    "buildingNumber": invoice.company.building_number,
                    "district": invoice.company.district,
                    "city": invoice.company.city,
                    "postalCode": invoice.company.postal_code,
                    "country": invoice.company.country
                }
            },
            "buyer": {
                "name": invoice.customer.name,
                "vatNumber": invoice.customer.vat_number or "",
                "address": {
                    "street": invoice.customer.street_name or "",
                    "buildingNumber": invoice.customer.building_number or "",
                    "district": invoice.customer.district or "",
                    "city": invoice.customer.city,
                    "postalCode": invoice.customer.postal_code or "",
                    "country": invoice.customer.country
                }
            },
            "invoiceLines": [
                {
                    "description": item.description,
                    "quantity": float(item.quantity),
                    "unitPrice": float(item.unit_price),
                    "vatRate": float(item.vat_rate),
                    "vatAmount": float(item.vat_amount),
                    "discount": float(item.discount),
                    "lineTotal": float(item.total)
                }
                for item in invoice.items.all()
            ],
            "totals": {
                "subtotal": float(invoice.subtotal),
                "vatAmount": float(invoice.vat_amount),
                "discount": float(invoice.discount),
                "total": float(invoice.total)
            }
        }
        return invoice_data
    
    def submit_invoice(self, invoice):
        """
        Submit invoice to ZATCA for approval
        """
        try:
            invoice_data = self.prepare_invoice_data(invoice)
            
            # Log the request
            log = ZATCALog.objects.create(
                invoice=invoice,
                action='submit_invoice',
                request_data=invoice_data
            )
            
            # Make API call
            response = requests.post(
                f"{self.api_url}/invoices",
                headers=self.headers,
                json=invoice_data,
                timeout=30
            )
            
            # Update log with response
            log.response_data = response.json() if response.content else {}
            log.status_code = response.status_code
            log.success = response.status_code == 200
            
            if response.status_code == 200:
                response_data = response.json()
                # Update invoice with ZATCA response
                invoice.uuid = response_data.get('uuid')
                invoice.qr_code = response_data.get('qrCode')
                invoice.zatca_response = response_data
                invoice.status = 'submitted'
                invoice.save()
                log.save()
                return True, "Invoice submitted successfully", response_data
            else:
                error_msg = f"ZATCA API Error: {response.status_code}"
                log.error_message = error_msg
                log.save()
                return False, error_msg, response.json() if response.content else {}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            if 'log' in locals():
                log.error_message = error_msg
                log.save()
            return False, error_msg, {}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if 'log' in locals():
                log.error_message = error_msg
                log.save()
            return False, error_msg, {}
    
    def check_invoice_status(self, invoice):
        """
        Check invoice status from ZATCA
        """
        if not invoice.uuid:
            return False, "Invoice not yet submitted to ZATCA", {}
        
        try:
            response = requests.get(
                f"{self.api_url}/invoices/{invoice.uuid}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, "Status retrieved", data
            else:
                return False, f"Error: {response.status_code}", {}
                
        except Exception as e:
            return False, f"Error: {str(e)}", {}
    
    def cancel_invoice(self, invoice, reason):
        """
        Cancel an invoice in ZATCA
        """
        if not invoice.uuid:
            return False, "Invoice not yet submitted to ZATCA", {}
        
        try:
            cancel_data = {
                "uuid": invoice.uuid,
                "reason": reason
            }
            
            log = ZATCALog.objects.create(
                invoice=invoice,
                action='cancel_invoice',
                request_data=cancel_data
            )
            
            response = requests.post(
                f"{self.api_url}/invoices/{invoice.uuid}/cancel",
                headers=self.headers,
                json=cancel_data,
                timeout=30
            )
            
            log.response_data = response.json() if response.content else {}
            log.status_code = response.status_code
            log.success = response.status_code == 200
            
            if response.status_code == 200:
                invoice.status = 'cancelled'
                invoice.save()
                log.save()
                return True, "Invoice cancelled successfully", response.json()
            else:
                error_msg = f"Error: {response.status_code}"
                log.error_message = error_msg
                log.save()
                return False, error_msg, {}
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if 'log' in locals():
                log.error_message = error_msg
                log.save()
            return False, error_msg, {}
    
    def generate_qr_code(self, invoice):
        """
        Generate QR code for simplified invoices
        """
        # TLV format for ZATCA QR Code
        # Tag 1: Seller name
        # Tag 2: VAT number
        # Tag 3: Timestamp
        # Tag 4: Total with VAT
        # Tag 5: VAT amount
        
        def encode_tlv(tag, value):
            value_bytes = value.encode('utf-8')
            length = len(value_bytes)
            return bytes([tag, length]) + value_bytes
        
        try:
            timestamp = f"{invoice.issue_date}T{invoice.issue_time}"
            
            tlv_data = b''
            tlv_data += encode_tlv(1, invoice.company.name)
            tlv_data += encode_tlv(2, invoice.company.vat_number)
            tlv_data += encode_tlv(3, timestamp)
            tlv_data += encode_tlv(4, str(invoice.total))
            tlv_data += encode_tlv(5, str(invoice.vat_amount))
            
            qr_code_b64 = base64.b64encode(tlv_data).decode('utf-8')
            return qr_code_b64
        except Exception as e:
            return None
