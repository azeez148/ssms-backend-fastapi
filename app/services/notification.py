# import pywhatkit
from sqlalchemy.orm import Session
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.core.config import settings
from app.core.utils import format_phone_number
from app.core.logging import logger
import emails
import firebase_admin
from firebase_admin import credentials, messaging
from app.schemas.day_management import DaySummary


# class WhatsAppNotificationService:
#     def send_sale_notification(self, sale: Sale):
#         """
#         Sends a sale confirmation message via pywhatkit.
#         """
#         if not (sale.customer and sale.customer.mobile):
#             print(f"No mobile number on sale #{sale.id}. Skipping notification.")
#             return
#
#         message_body = (
#             f"Hi {sale.customer.name},\n\n"
#             f"Your sale (ID: #{sale.id}) for ₹{sale.total_price:,.2f} has been confirmed.\n\n"
#             "Thank you for your purchase!"
#         )
#
#         if sale.shop:
#             message_body += "\n\nFollow us for updates and offers:"
#             if sale.shop.instagram_link:
#                 message_body += f"\nInstagram: {sale.shop.instagram_link}"
#             if sale.shop.whatsapp_group_link:
#                 message_body += f"\nWhatsApp Group: {sale.shop.whatsapp_group_link}"
#             if sale.shop.website_link:
#                 message_body += f"\nWebsite: {sale.shop.website_link}"
#
#         try:
#             phone_number = format_phone_number(sale.customer.mobile)
#             pywhatkit.sendwhatmsg_instantly(phone_number, message_body, wait_time=15, tab_close=True, close_time=3)
#             print(f"Successfully sent WhatsApp sale notification to {sale.customer.mobile}")
#         except ValueError as e:
#             print(f"Invalid phone number for sale #{sale.id}: {e}")
#         except Exception as e:
#             print(f"An unexpected error occurred while sending WhatsApp message: {e}")
#
#     def send_day_summary_notification(self, day_summary: DaySummary, to_phone_number: str):
#         """
#         Sends an end-of-day summary notification via WhatsApp.
#         """
#         message_body = (
#             f"End of Day Summary for {day_summary.start_time.strftime('%Y-%m-%d')}:\n\n"
#             f"Opening Balance: ₹{day_summary.opening_balance:,.2f}\n"
#             f"Closing Balance: ₹{day_summary.closing_balance:,.2f}\n"
#             f"Total Sales: ₹{(day_summary.cash_in_hand + day_summary.cash_in_account):,.2f}\n"
#             f"  - Cash in Hand: ₹{day_summary.cash_in_hand:,.2f}\n"
#             f"  - Cash in Account: ₹{day_summary.cash_in_account:,.2f}\n"
#             f"Total Expenses: ₹{day_summary.total_expense:,.2f}\n\n"
#             "Day ended successfully."
#         )
#
#         try:
#             phone_number = format_phone_number(to_phone_number)
#             pywhatkit.sendwhatmsg_instantly(phone_number, message_body, wait_time=15, tab_close=True, close_time=3)
#             print(f"Successfully sent day summary WhatsApp notification to {phone_number}")
#         except Exception as e:
#             print(f"An unexpected error occurred while sending day summary WhatsApp message: {e}")


class EmailNotificationService:
    def send_sale_notification(self, sale_data: dict):
        # sale_data is now a dict (from Kafka or direct)
        customer = sale_data.get('customer')
        if not customer:
            return

        items = sale_data.get('sale_items', [])
        items_html = "".join([
            f"<tr><td>{item.get('product_name')}</td><td>{item.get('size')}</td><td>{item.get('quantity')}</td><td>{item.get('sale_price')}</td></tr>"
            for item in items
        ])

        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer.get('name', 'Customer')

        html_content = f"""
        <h1>Sale Confirmation</h1>
        <p>Dear {customer_name},</p>
        <p>Thank you for your purchase. Here are the details of your order:</p>
        <p><strong>Order ID:</strong> {sale_data.get('id')}</p>
        <p><strong>Date:</strong> {sale_data.get('date')}</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Size</th>
                    <th>Quantity</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        <p><strong>Total Quantity:</strong> {sale_data.get('total_quantity')}</p>
        <p><strong>Total Price:</strong> {sale_data.get('total_price')}</p>
        <p><strong>Payment Method:</strong> {sale_data.get('payment_type', {}).get('name') if sale_data.get('payment_type') else 'N/A'}</p>
        <p><strong>Delivery Method:</strong> {sale_data.get('delivery_type', {}).get('name') if sale_data.get('delivery_type') else 'N/A'}</p>
        <p>Thank you for shopping with us!</p>
        """

        message = emails.Message(
            subject=f"Sale Confirmation #{sale_data.get('id')}",
            html=html_content,
            mail_from=(settings.MAIL_FROM, settings.MAIL_FROM),
        )

        smtp_options = {
            "host": settings.MAIL_SERVER,
            "port": settings.MAIL_PORT,
            "tls": settings.MAIL_TLS,
            "ssl": settings.MAIL_SSL,
            "user": settings.MAIL_USERNAME,
            "password": settings.MAIL_PASSWORD,
        }

        email = customer.get('email')
        if email:
            response = message.send(to=email, smtp=smtp_options)
            if not response.success:
                logger.error(f"Failed to send email to {email}: {response.error}")
        
        # Also send a notification to the shop owner if email is available
        if settings.ADMIN_EMAIL:
            response = message.send(to=settings.ADMIN_EMAIL, smtp=smtp_options)
            if not response.success:
                logger.error(f"Failed to send email to shop owner {settings.ADMIN_EMAIL}: {response.error}")

    def send_purchase_notification(self, purchase_data: dict):
        vendor = purchase_data.get('vendor')
        if not vendor or not vendor.get('email'):
            return

        items = purchase_data.get('purchase_items', [])
        items_html = "".join([
            f"<tr><td>{item.get('product_name')}</td><td>{item.get('size')}</td><td>{item.get('quantity')}</td><td>{item.get('purchase_price')}</td></tr>"
            for item in items
        ])

        html_content = f"""
        <h1>Purchase Confirmation</h1>
        <p>Dear {vendor.get('name')},</p>
        <p>A new purchase has been made. Here are the details:</p>
        <p><strong>Purchase ID:</strong> {purchase_data.get('id')}</p>
        <p><strong>Date:</strong> {purchase_data.get('date')}</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>Product</th>
                    <th>Size</th>
                    <th>Quantity</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        <p><strong>Total Quantity:</strong> {purchase_data.get('total_quantity')}</p>
        <p><strong>Total Price:</strong> {purchase_data.get('total_price')}</p>
        <p><strong>Payment Method:</strong> {purchase_data.get('payment_type', {}).get('name') if purchase_data.get('payment_type') else 'N/A'}</p>
        <p><strong>Delivery Method:</strong> {purchase_data.get('delivery_type', {}).get('name') if purchase_data.get('delivery_type') else 'N/A'}</p>
        <p>Thank you!</p>
        """

        message = emails.Message(
            subject=f"Purchase Confirmation #{purchase_data.get('id')}",
            html=html_content,
            mail_from=(settings.MAIL_FROM, settings.MAIL_FROM),
        )

        smtp_options = {
            "host": settings.MAIL_SERVER,
            "port": settings.MAIL_PORT,
            "tls": settings.MAIL_TLS,
            "ssl": settings.MAIL_SSL,
            "user": settings.MAIL_USERNAME,
            "password": settings.MAIL_PASSWORD,
        }

        email = vendor.get('email')
        response = message.send(to=email, smtp=smtp_options)
        if not response.success:
            logger.error(f"Failed to send email to {email}: {response.error}")

    def send_day_summary_notification(self, day_summary_data: dict):
        """
        Sends an end-of-day summary email to the admin.
        """
        expenses = day_summary_data.get('expenses', [])
        expenses_html = "".join([
            f"<tr><td>{expense.get('description')}</td><td>{expense.get('amount')}</td></tr>"
            for expense in expenses
        ])

        start_time = day_summary_data.get('start_time')
        end_time = day_summary_data.get('end_time')

        html_content = f"""
        <h1>End of Day Summary</h1>
        <p>Here is the summary for the day ending on {end_time}:</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tbody>
                <tr><td>Opening Balance</td><td>{day_summary_data.get('opening_balance', 0):,.2f}</td></tr>
                <tr><td>Closing Balance</td><td>{day_summary_data.get('closing_balance', 0):,.2f}</td></tr>
                <tr><td>Total Sales</td><td>{(day_summary_data.get('cash_in_hand', 0) + day_summary_data.get('cash_in_account', 0)):,.2f}</td></tr>
                <tr><td>&nbsp;&nbsp;- Cash in Hand</td><td>{day_summary_data.get('cash_in_hand', 0):,.2f}</td></tr>
                <tr><td>&nbsp;&nbsp;- Cash in Account</td><td>{day_summary_data.get('cash_in_account', 0):,.2f}</td></tr>
                <tr><td>Total Expenses</td><td>{day_summary_data.get('total_expense', 0):,.2f}</td></tr>
            </tbody>
        </table>
        <h2>Expenses Details</h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {expenses_html}
            </tbody>
        </table>
        <p>Day ended successfully.</p>
        """

        message = emails.Message(
            subject=f"End of Day Summary - {start_time}",
            html=html_content,
            mail_from=(settings.MAIL_FROM, settings.MAIL_FROM),
        )

        smtp_options = {
            "host": settings.MAIL_SERVER,
            "port": settings.MAIL_PORT,
            "tls": settings.MAIL_TLS,
            "ssl": settings.MAIL_SSL,
            "user": settings.MAIL_USERNAME,
            "password": settings.MAIL_PASSWORD,
        }

        response = message.send(to=settings.MAIL_FROM, smtp=smtp_options)
        if not response.success:
            logger.error(f"Failed to send day summary email to {settings.MAIL_FROM}: {response.error}")


class PushNotificationService:
    def __init__(self):
        self._initialize_firebase()

    def _initialize_firebase(self):
        try:
            if not firebase_admin._apps:
                if settings.FCM_CREDENTIALS_FILE:
                    cred = credentials.Certificate(settings.FCM_CREDENTIALS_FILE)
                    firebase_admin.initialize_app(cred)
                else:
                    # Fallback to default credentials if file not specified
                    # This might fail if no environment variables are set, but it allows for extension
                    try:
                        firebase_admin.initialize_app()
                    except Exception:
                        logger.warning("Firebase Admin SDK not initialized: Missing credentials.")
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin SDK: {e}")

    def send_push_notification(self, title: str, body: str, data: dict = None):
        """
        Sends push notifications to the admin app using FCM.
        """
        logger.info(f"Sending push notification: {title} - {body}")

        if not firebase_admin._apps:
            logger.warning("Cannot send push notification: Firebase app not initialized.")
            return

        try:
            # Prepare data payload (convert all values to strings as FCM requires)
            data_payload = {}
            if data:
                for key, value in data.items():
                    if isinstance(value, (dict, list)):
                        import json
                        data_payload[key] = json.dumps(value)
                    else:
                        data_payload[key] = str(value)

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data_payload,
                topic=settings.FCM_ADMIN_TOPIC,
            )

            response = messaging.send(message)
            logger.info(f"Successfully sent FCM message: {response}")
        except Exception as e:
            logger.error(f"Error sending FCM message: {e}")

    def notify_sale_event(self, event_type: str, payload: dict):
        sale_id = payload.get('id')
        total_price = payload.get('total_price')
        title = f"Sale {event_type.replace('_', ' ').title()}"
        body = f"Sale #{sale_id} for ₹{total_price:,.2f}"
        self.send_push_notification(title, body, payload)

    def notify_day_event(self, event_type: str, payload: dict):
        title = f"Day {event_type.replace('_', ' ').title()}"
        if event_type == "expense_added":
            body = f"Expense added: {payload.get('description')} - ₹{payload.get('amount'):,.2f}"
        else:
            body = f"Day management event occurred: {event_type}"
        self.send_push_notification(title, body, payload)
