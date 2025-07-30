from app.models.sale import Sale
from app.core.config import settings
import emails
import pywhatkit

class WhatsAppNotificationService:
    def send_sale_notification(self, sale: Sale):
        if sale.customer_mobile:
            try:
                pywhatkit.sendwhatmsg_instantly(
                    phone_no=sale.customer_mobile,
                    message=f"Hi {sale.customer_name}, your sale with ID #{sale.id} has been confirmed. Total amount: {sale.total_price}"
                )
            except Exception as e:
                print(f"Failed to send WhatsApp message to {sale.customer_mobile}: {e}")

class EmailNotificationService:
    def send_sale_notification(self, sale: Sale):
        message = emails.Message(
            subject=f"Sale Confirmation #{sale.id}",
            html=f"""
            <h1>Sale Confirmation</h1>
            <p>Dear {sale.customer_name},</p>
            <p>Thank you for your purchase. Here are the d
            etails of your order:</p>
            <ul>
                <li><strong>Order ID:</strong> {sale.id}</li>
                <li><strong>Total Quantity:</strong> {sale.total_quantity}</li>
                <li><strong>Total Price:</strong> {sale.total_price}</li>
            </ul>
            <p>Thank you for shopping with us!</p>
            """,
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

        if sale.customer_email:
            response = message.send(to=sale.customer_email, smtp=smtp_options)
            if not response.success:
                print(f"Failed to send email to {sale.customer_email}: {response.error}")
