import os
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.product import Product
from app.core.config import settings
import emails
import httpx
# class WhatsAppNotificationService:
#     def send_sale_notification(self, sale: Sale):
#         if sale.customer and sale.customer.mobile:
#             try:
#                 pywhatkit.sendwhatmsg_instantly(
#                     phone_no=sale.customer.mobile,
#                     message=f"Hi {sale.customer.name}, your sale with ID #{sale.id} has been confirmed. Total amount: {sale.total_price}"
#                 )
#             except Exception as e:
#                 print(f"Failed to send WhatsApp message to {sale.customer.mobile}: {e}")



class WhatsAppNotificationService:
    # Get credentials from environment variables.
    # Set these in your Render service's "Environment" tab.
    WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
    PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    def send_sale_notification(self, sale: Sale):
        """
        Sends a sale confirmation message via the WhatsApp Business API.
        """
        # 1. Check if the service is configured and if the customer has a mobile number.
        if not self.WHATSAPP_API_TOKEN or not self.PHONE_NUMBER_ID:
            print("WhatsApp service is not configured. Skipping notification.")
            return

        if not (sale.customer and sale.customer.mobile):
            print(f"No mobile number on sale #{sale.id}. Skipping notification.")
            return

        # 2. Prepare the API request details.
        api_url = f"https://graph.facebook.com/v20.0/{self.PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }

        # Construct a clear, user-friendly message.
        message_body = (
            f"Hi {sale.customer.name},\n\n"
            f"Your sale (ID: #{sale.id}) for ₹{sale.total_price:,.2f} has been confirmed.\n\n"
            "Thank you for your purchase!"
        )

        payload = {
            "messaging_product": "whatsapp",
            "to": sale.customer.mobile,  # Ensure this number includes the country code, e.g., 919876543210
            "type": "text",
            "text": {"body": message_body},
        }

        # 3. Send the message using httpx.
        try:
            with httpx.Client() as client:
                response = client.post(api_url, headers=headers, json=payload)
                # Raise an exception for HTTP error codes (4xx or 5xx)
                response.raise_for_status()
            
            print(f"Successfully sent WhatsApp sale notification to {sale.customer.mobile}")

        except httpx.HTTPStatusError as e:
            # Handle API-specific errors
            print(f"Failed to send WhatsApp message. Status: {e.response.status_code}. Response: {e.response.text}")
        except Exception as e:
            # Handle other errors like network issues
            print(f"An unexpected error occurred while sending WhatsApp message: {e}")


class EmailNotificationService:
    def send_sale_notification(self, sale: Sale):
        if not sale.customer:
            return

        items_html = "".join([
            f"<tr><td>{item.product_name}</td><td>{item.size}</td><td>{item.quantity}</td><td>{item.sale_price}</td></tr>"
            for item in sale.sale_items
        ])

        html_content = f"""
        <h1>Sale Confirmation</h1>
        <p>Dear {sale.customer.name},</p>
        <p>Thank you for your purchase. Here are the details of your order:</p>
        <p><strong>Order ID:</strong> {sale.id}</p>
        <p><strong>Date:</strong> {sale.date}</p>
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
        <p><strong>Total Quantity:</strong> {sale.total_quantity}</p>
        <p><strong>Total Price:</strong> {sale.total_price}</p>
        <p><strong>Payment Method:</strong> {sale.payment_type.name if sale.payment_type else 'N/A'}</p>
        <p><strong>Delivery Method:</strong> {sale.delivery_type.name if sale.delivery_type else 'N/A'}</p>
        <p>Thank you for shopping with us!</p>
        """

        message = emails.Message(
            subject=f"Sale Confirmation #{sale.id}",
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

        if sale.customer.email:
            response = message.send(to=sale.customer.email, smtp=smtp_options)
            if not response.success:
                print(f"Failed to send email to {sale.customer.email}: {response.error}")

    def send_purchase_notification(self, purchase: Purchase):
        if not purchase.vendor or not purchase.vendor.email:
            return

        items_html = "".join([
            f"<tr><td>{item.product_name}</td><td>{item.size}</td><td>{item.quantity}</td><td>{item.purchase_price}</td></tr>"
            for item in purchase.purchase_items
        ])

        html_content = f"""
        <h1>Purchase Confirmation</h1>
        <p>Dear {purchase.vendor.name},</p>
        <p>A new purchase has been made. Here are the details:</p>
        <p><strong>Purchase ID:</strong> {purchase.id}</p>
        <p><strong>Date:</strong> {purchase.date}</p>
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
        <p><strong>Total Quantity:</strong> {purchase.total_quantity}</p>
        <p><strong>Total Price:</strong> {purchase.total_price}</p>
        <p><strong>Payment Method:</strong> {purchase.payment_type.name if purchase.payment_type else 'N/A'}</p>
        <p><strong>Delivery Method:</strong> {purchase.delivery_type.name if purchase.delivery_type else 'N/A'}</p>
        <p>Thank you!</p>
        """

        message = emails.Message(
            subject=f"Purchase Confirmation #{purchase.id}",
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

        response = message.send(to=purchase.vendor.email, smtp=smtp_options)
        if not response.success:
            print(f"Failed to send email to {purchase.vendor.email}: {response.error}")
