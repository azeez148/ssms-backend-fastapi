import pywhatkit
from sqlalchemy.orm import Session
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.core.config import settings
from app.core.utils import format_phone_number
import emails
from app.schemas.day_management import DaySummary


class WhatsAppNotificationService:
    def send_sale_notification(self, sale: Sale):
        """
        Sends a sale confirmation message via pywhatkit.
        """
        if not (sale.customer and sale.customer.mobile):
            print(f"No mobile number on sale #{sale.id}. Skipping notification.")
            return

        message_body = (
            f"Hi {sale.customer.name},\n\n"
            f"Your sale (ID: #{sale.id}) for ₹{sale.total_price:,.2f} has been confirmed.\n\n"
            "Thank you for your purchase!"
        )

        if sale.shop:
            message_body += "\n\nFollow us for updates and offers:"
            if sale.shop.instagram_link:
                message_body += f"\nInstagram: {sale.shop.instagram_link}"
            if sale.shop.whatsapp_group_link:
                message_body += f"\nWhatsApp Group: {sale.shop.whatsapp_group_link}"
            if sale.shop.website_link:
                message_body += f"\nWebsite: {sale.shop.website_link}"

        try:
            phone_number = format_phone_number(sale.customer.mobile)
            pywhatkit.sendwhatmsg_instantly(phone_number, message_body, wait_time=15, tab_close=True, close_time=3)
            print(f"Successfully sent WhatsApp sale notification to {sale.customer.mobile}")
        except ValueError as e:
            print(f"Invalid phone number for sale #{sale.id}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while sending WhatsApp message: {e}")

    def send_day_summary_notification(self, day_summary: DaySummary, to_phone_number: str):
        """
        Sends an end-of-day summary notification via WhatsApp.
        """
        message_body = (
            f"End of Day Summary for {day_summary.start_time.strftime('%Y-%m-%d')}:\n\n"
            f"Opening Balance: ₹{day_summary.opening_balance:,.2f}\n"
            f"Closing Balance: ₹{day_summary.closing_balance:,.2f}\n"
            f"Total Sales: ₹{(day_summary.cash_in_hand + day_summary.cash_in_account):,.2f}\n"
            f"  - Cash in Hand: ₹{day_summary.cash_in_hand:,.2f}\n"
            f"  - Cash in Account: ₹{day_summary.cash_in_account:,.2f}\n"
            f"Total Expenses: ₹{day_summary.total_expense:,.2f}\n\n"
            "Day ended successfully."
        )

        try:
            phone_number = format_phone_number(to_phone_number)
            pywhatkit.sendwhatmsg_instantly(phone_number, message_body, wait_time=15, tab_close=True, close_time=3)
            print(f"Successfully sent day summary WhatsApp notification to {phone_number}")
        except Exception as e:
            print(f"An unexpected error occurred while sending day summary WhatsApp message: {e}")


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
        <p>Dear {sale.customer.first_name} {sale.customer.last_name},</p>
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

    def send_day_summary_notification(self, day_summary: DaySummary):
        """
        Sends an end-of-day summary email to the admin.
        """
        expenses_html = "".join([
            f"<tr><td>{expense.description}</td><td>{expense.amount}</td></tr>"
            for expense in day_summary.expenses
        ])

        html_content = f"""
        <h1>End of Day Summary</h1>
        <p>Here is the summary for the day ending on {day_summary.end_time.strftime('%Y-%m-%d %H:%M:%S')}:</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <tbody>
                <tr><td>Opening Balance</td><td>{day_summary.opening_balance:,.2f}</td></tr>
                <tr><td>Closing Balance</td><td>{day_summary.closing_balance:,.2f}</td></tr>
                <tr><td>Total Sales</td><td>{(day_summary.cash_in_hand + day_summary.cash_in_account):,.2f}</td></tr>
                <tr><td>&nbsp;&nbsp;- Cash in Hand</td><td>{day_summary.cash_in_hand:,.2f}</td></tr>
                <tr><td>&nbsp;&nbsp;- Cash in Account</td><td>{day_summary.cash_in_account:,.2f}</td></tr>
                <tr><td>Total Expenses</td><td>{day_summary.total_expense:,.2f}</td></tr>
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
            subject=f"End of Day Summary - {day_summary.start_time.strftime('%Y-%m-%d')}",
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
            print(f"Failed to send day summary email to {settings.MAIL_FROM}: {response.error}")
