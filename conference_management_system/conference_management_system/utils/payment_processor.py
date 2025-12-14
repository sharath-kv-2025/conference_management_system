import frappe
import random
import uuid
import json
from datetime import datetime

class PaymentProcessor:
    """Mock payment processor with comprehensive payment tracking"""
    
    @staticmethod
    def process_payment(registration_id, payment_method="Credit Card", payment_data=None):
        """
        Process payment for a registration with complete mock data
        Returns: dict with payment result
        """
        try:
            registration = frappe.get_doc("Registration", registration_id)
            
            # Generate mock payment details based on method
            mock_details = PaymentProcessor._generate_mock_payment_details(payment_method, payment_data)
            
            # Mock payment processing scenarios
            payment_scenarios = [
                {"success": True, "message": "Payment processed successfully", "gateway_code": "00"},
                {"success": True, "message": "Payment completed via UPI", "gateway_code": "00"},
                {"success": True, "message": "Card payment successful", "gateway_code": "00"},
                {"success": False, "message": "Insufficient funds", "gateway_code": "51"},
                {"success": False, "message": "Card declined", "gateway_code": "05"},
                {"success": False, "message": "Network timeout", "gateway_code": "91"},
            ]
            
            # 80% success rate for demo
            weights = [0.3, 0.25, 0.25, 0.08, 0.07, 0.05]
            result = random.choices(payment_scenarios, weights=weights)[0]
            
            # Generate transaction IDs
            transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
            gateway_txn_id = f"GW_{uuid.uuid4().hex[:16].upper()}"
            
            # Calculate fees
            processing_fee = round(registration.amount * 0.025, 2)  # 2.5% processing fee
            net_amount = registration.amount - processing_fee
            
            # Create comprehensive payment record
            payment_details = PaymentProcessor._create_payment_record(
                registration_id, transaction_id, gateway_txn_id, payment_method,
                registration.amount, processing_fee, net_amount, result, mock_details
            )
            
            if result["success"]:
                # Update registration status and link payment details
                registration.payment_status = "Paid"
                if payment_details:
                    registration.payment_details = payment_details.name
                registration.save()
                frappe.db.commit()
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "gateway_transaction_id": gateway_txn_id,
                    "amount": registration.amount,
                    "processing_fee": processing_fee,
                    "net_amount": net_amount,
                    "payment_method": payment_method,
                    "payment_details": payment_details.name,
                    "message": result["message"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Update registration status and link payment details
                registration.payment_status = "Failed"
                if payment_details:
                    registration.payment_details = payment_details.name
                registration.save()
                frappe.db.commit()
                
                return {
                    "success": False,
                    "transaction_id": transaction_id,
                    "gateway_transaction_id": gateway_txn_id,
                    "error": result["message"],
                    "payment_details": payment_details.name,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            frappe.log_error(f"Payment processing error: {str(e)}", "Payment Processor")
            return {
                "success": False,
                "error": "Payment processing failed due to system error"
            }
    
    @staticmethod
    def _generate_mock_payment_details(payment_method, payment_data):
        """Generate realistic mock payment details based on method"""
        details = {}
        
        if payment_method in ["Credit Card", "Debit Card"]:
            card_types = ["Visa", "MasterCard", "RuPay", "American Express"]
            banks = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Bank"]
            
            details.update({
                "card_last_four": str(random.randint(1000, 9999)),
                "card_type": random.choice(card_types),
                "bank_name": random.choice(banks)
            })
            
        elif payment_method == "UPI":
            upi_providers = ["@paytm", "@phonepe", "@googlepay", "@amazonpay"]
            details.update({
                "upi_id": f"user{random.randint(1000, 9999)}{random.choice(upi_providers)}"
            })
            
        elif payment_method == "Net Banking":
            banks = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Bank"]
            details.update({
                "bank_name": random.choice(banks)
            })
            
        return details
    
    @staticmethod
    def _create_payment_record(registration_id, transaction_id, gateway_txn_id, payment_method, 
                             amount, processing_fee, net_amount, result, mock_details):
        """Create comprehensive payment record"""
        try:
            payment_doc = frappe.new_doc("Mock Payment Details")
            payment_doc.registration = registration_id
            payment_doc.transaction_id = transaction_id
            payment_doc.gateway_transaction_id = gateway_txn_id
            payment_doc.payment_method = payment_method
            payment_doc.amount = amount
            payment_doc.processing_fee = processing_fee
            payment_doc.net_amount = net_amount
            payment_doc.payment_status = "Success" if result["success"] else "Failed"
            
            # Add method-specific details
            if mock_details.get("card_last_four"):
                payment_doc.card_last_four = mock_details["card_last_four"]
                payment_doc.card_type = mock_details["card_type"]
                payment_doc.bank_name = mock_details["bank_name"]
            elif mock_details.get("upi_id"):
                payment_doc.upi_id = mock_details["upi_id"]
            elif mock_details.get("bank_name"):
                payment_doc.bank_name = mock_details["bank_name"]
            
            # Mock gateway response
            gateway_response = {
                "status": "success" if result["success"] else "failed",
                "message": result["message"],
                "gateway_code": result["gateway_code"],
                "transaction_id": gateway_txn_id,
                "timestamp": datetime.now().isoformat()
            }
            payment_doc.gateway_response = json.dumps(gateway_response, indent=2)
            
            if not result["success"]:
                payment_doc.failure_reason = result["message"]
            
            payment_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            return payment_doc
            
        except Exception as e:
            frappe.log_error(f"Failed to create payment record: {str(e)}", "Payment Processor")
            return None
    

    
