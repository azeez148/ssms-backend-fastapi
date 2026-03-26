import firebase_admin
from firebase_admin import credentials, messaging
import json
import os
from typing import List, Optional, Dict, Any
from app.core.config import settings
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_device import UserDevice
from app.core.logging import logger

class PushNotificationService:
    _initialized = False

    def __init__(self):
        if not PushNotificationService._initialized:
            self._initialize_firebase()

    def _initialize_firebase(self):
        try:
            service_account_json = settings.FIREBASE_SERVICE_ACCOUNT_JSON
            if service_account_json:
                # Can be a path or a JSON string
                if os.path.exists(service_account_json):
                    cred = credentials.Certificate(service_account_json)
                else:
                    try:
                        service_account_info = json.loads(service_account_json)
                        cred = credentials.Certificate(service_account_info)
                    except json.JSONDecodeError:
                        logger.error("FIREBASE_SERVICE_ACCOUNT_JSON is neither a valid path nor a valid JSON string.")
                        return

                firebase_admin.initialize_app(cred)
                PushNotificationService._initialized = True
                logger.info("Firebase Admin SDK initialized successfully.")
            else:
                logger.warning("FIREBASE_SERVICE_ACCOUNT_JSON not provided. Push notifications will be disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")

    def send_push_notification(self, tokens: List[str], title: str, body: str, data: Optional[Dict[str, str]] = None):
        if not PushNotificationService._initialized or not tokens:
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            tokens=tokens,
        )
        try:
            response = messaging.send_multicast(message)
            if response.failure_count > 0:
                responses = response.responses
                failed_tokens = []
                for idx, resp in enumerate(responses):
                    if not resp.success:
                        # The order of responses corresponds to the order of the tokens.
                        failed_tokens.append(tokens[idx])
                logger.warning(f"Failed to send push notifications to {len(failed_tokens)} tokens.")
            logger.info(f"Successfully sent {response.success_count} push notifications.")
            return response
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return None

    def send_to_admin(self, db: Session, title: str, body: str, data: Optional[Dict[str, str]] = None):
        # Get all admin users
        admins = db.query(User).filter(User.role == 'admin').all()
        tokens = []
        for admin in admins:
            for device in admin.devices:
                tokens.append(device.fcm_token)

        if tokens:
            self.send_push_notification(tokens, title, body, data)
        else:
            logger.info("No admin devices found to send push notification.")

    # Specific notification methods to match existing email ones
    def send_sale_created_push(self, db: Session, sale):
        title = f"🚨 New Sale Notification - Order #{sale.id}"
        body = f"Customer: {sale.customer.name if sale.customer else 'N/A'}\nTotal: ₹{sale.total_price}\nItems: {sale.total_quantity}"
        self.send_to_admin(db, title, body, {"sale_id": str(sale.id), "type": "sale_created"})

    def send_sale_cancelled_push(self, db: Session, sale):
        title = f"❌ Sale Cancelled - Order #{sale.id}"
        body = f"Order for {sale.customer.name if sale.customer else 'N/A'} of ₹{sale.total_price} has been cancelled."
        self.send_to_admin(db, title, body, {"sale_id": str(sale.id), "type": "sale_cancelled"})

    def send_sale_status_change_push(self, db: Session, sale, old_status, new_status):
        title = f"🔄 Sale Status Updated - Order #{sale.id}"
        body = f"Status changed from {old_status} to {new_status}."
        self.send_to_admin(db, title, body, {"sale_id": str(sale.id), "type": "sale_status_change"})

    def send_day_start_push(self, db: Session, day):
        title = "☀️ New Day Started"
        body = f"Opening Balance: ₹{day.opening_balance:,.2f}\nTime: {day.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        self.send_to_admin(db, title, body, {"day_id": str(day.id), "type": "day_start"})

    def send_expense_added_push(self, db: Session, expense):
        title = "💸 New Expense Added"
        body = f"Description: {expense.description}\nAmount: ₹{expense.amount:,.2f}"
        self.send_to_admin(db, title, body, {"expense_id": str(expense.id), "type": "expense_added"})

    def send_customer_added_push(self, db: Session, customer):
        title = "👤 New Customer Registered"
        body = f"Name: {customer.name}\nMobile: {customer.mobile}"
        self.send_to_admin(db, title, body, {"customer_id": str(customer.id), "type": "customer_added"})

    def send_product_added_push(self, db: Session, product):
        title = "📦 New Product Added"
        body = f"Name: {product.name}\nPrice: ₹{product.selling_price}"
        self.send_to_admin(db, title, body, {"product_id": str(product.id), "type": "product_added"})

    def send_product_stock_updated_push(self, db: Session, product, size, quantity_change):
        title = "📉 Product Stock Updated"
        body = f"Product: {product.name}\nSize: {size}\nChange: {quantity_change}"
        self.send_to_admin(db, title, body, {"product_id": str(product.id), "type": "stock_update"})

    def send_day_summary_push(self, db: Session, day_summary):
        title = "📊 End of Day Summary"
        total_sales = day_summary.cash_in_hand + day_summary.cash_in_account
        body = f"Total Sales: ₹{total_sales:,.2f}\nExpenses: ₹{day_summary.total_expense:,.2f}\nClosing: ₹{day_summary.closing_balance:,.2f}"
        self.send_to_admin(db, title, body, {"type": "day_summary"})
