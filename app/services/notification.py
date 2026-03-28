# import pywhatkit
from sqlalchemy.orm import Session
from typing import List
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.customer import Customer
from app.models.event import EventOffer
from app.models.product import Product
from app.models.day_management import Day, Expense
from app.models.shop import Shop
from app.core.config import settings
from app.core.logging import logger
from app.core.utils import format_phone_number
import emails
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
    def __init__(self):
        self.smtp_options = {
            "host": settings.MAIL_SERVER,
            "port": settings.MAIL_PORT,
            "tls": settings.MAIL_TLS,
            "ssl": settings.MAIL_SSL,
            "user": settings.MAIL_USERNAME,
            "password": settings.MAIL_PASSWORD,
        }

    def _send_email(self, to_email: str, subject: str, html_content: str):
        message = emails.Message(
            subject=subject,
            html=html_content,
            mail_from=(settings.MAIL_FROM, settings.MAIL_FROM),
        )
        response = message.send(to=to_email, smtp=self.smtp_options)
        if not response.success:
            logger.error(f"Failed to send email to {to_email}: {response.error}")
        return response

    def send_sale_created_notification(self, sale: Sale):
        if not sale.customer:
            return

        items_html = "".join([
            f"<tr><td>{item.product_name}</td><td>{item.size}</td><td>{item.quantity}</td><td>{item.sale_price}</td></tr>"
            for item in sale.sale_items
        ])

        customer_html_content = f"""
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

        admin_html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width:700px; margin:auto; border:1px solid #ddd; padding:20px">

            <div style="background:#111; color:white; padding:15px; text-align:center">
                <h2>🚨 New Sale Notification</h2>
                <p>Adrenaline Sports Store</p>
            </div>

            <br>

            <h3>Order Details</h3>

            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td><strong>Order ID</strong></td>
                    <td>{sale.id}</td>
                </tr>
                <tr>
                    <td><strong>Customer</strong></td>
                    <td>{sale.customer.name}</td>
                </tr>
                <tr>
                    <td><strong>Date</strong></td>
                    <td>{sale.date}</td>
                </tr>
                <tr>
                    <td><strong>Payment Method</strong></td>
                    <td>{sale.payment_type.name if sale.payment_type else 'N/A'}</td>
                </tr>
                <tr>
                    <td><strong>Delivery Method</strong></td>
                    <td>{sale.delivery_type.name if sale.delivery_type else 'N/A'}</td>
                </tr>
            </table>

            <br>

            <h3>Items Sold</h3>

            <table border="1" cellpadding="8" cellspacing="0"
                style="width:100%; border-collapse:collapse; text-align:left">
                <thead style="background:#f5f5f5;">
                    <tr>
                        <th>Product</th>
                        <th>Size</th>
                        <th>Qty</th>
                        <th>Price</th>
                    </tr>
                </thead>

                <tbody>
                    {items_html}
                </tbody>
            </table>

            <br>

            <div style="background:#f9f9f9; padding:15px; border:1px solid #eee;">
                <p><strong>Total Quantity:</strong> {sale.total_quantity}</p>
                <p><strong>Total Price:</strong> ₹{sale.total_price}</p>
            </div>

            <br>

            <p style="color:#777; font-size:13px;">
                This is an automated sale alert generated from the billing system.
            </p>

        </div>
        """

        if sale.customer.email:
            self._send_email(sale.customer.email, f"Sale Confirmation #{sale.id}", customer_html_content)

        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"New Sale Confirmation #{sale.id}", admin_html_content)

    def send_sale_notification(self, sale: Sale):
        # Alias for backward compatibility or if called elsewhere
        self.send_sale_created_notification(sale)

    def send_sale_cancelled_notification(self, sale: Sale):
        if not sale.customer:
            return

        html_content = f"""
        <h1>Sale Cancelled</h1>
        <p>Dear {sale.customer.name},</p>
        <p>Your order #{sale.id} has been cancelled.</p>
        <p><strong>Total Price:</strong> ₹{sale.total_price}</p>
        <p>If you have any questions, please contact us.</p>
        """

        if sale.customer.email:
            self._send_email(sale.customer.email, f"Sale Cancelled #{sale.id}", html_content)

        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Sale Cancelled #{sale.id}", html_content)

    def send_sale_status_change_notification(self, sale: Sale, old_status: str, new_status: str):
        if not sale.customer:
            return

        html_content = f"""
        <h1>Sale Status Updated</h1>
        <p>Dear {sale.customer.name},</p>
        <p>The status of your order #{sale.id} has been changed from <strong>{old_status}</strong> to <strong>{new_status}</strong>.</p>
        <p>Thank you for your patience!</p>
        """

        if sale.customer.email:
            self._send_email(sale.customer.email, f"Order #{sale.id} Status Updated", html_content)
        
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Order #{sale.id} Status Updated", html_content)

    def send_day_start_notification(self, day: Day):
        html_content = f"""
        <h1>New Day Started</h1>
        <p>A new business day has been started.</p>
        <p><strong>Start Time:</strong> {day.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Opening Balance:</strong> ₹{day.opening_balance:,.2f}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, "New Day Started Notification", html_content)

    def send_expense_added_notification(self, expense: Expense):
        html_content = f"""
        <h1>New Expense Added</h1>
        <p>A new expense has been recorded.</p>
        <p><strong>Description:</strong> {expense.description}</p>
        <p><strong>Amount:</strong> ₹{expense.amount:,.2f}</p>
        <p><strong>Date:</strong> {expense.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, "New Expense Notification", html_content)

    def send_customer_added_notification(self, customer: Customer):
        html_content = f"""
        <h1>New Customer Added</h1>
        <p>A new customer has been registered in the system.</p>
        <p><strong>Name:</strong> {customer.name}</p>
        <p><strong>Mobile:</strong> {customer.mobile}</p>
        <p><strong>Email:</strong> {customer.email or 'N/A'}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, "New Customer Registered", html_content)

    def send_offer_created_notification(self, offer: EventOffer):
        html_content = f"""
        <h1>New Offer Created</h1>
        <p>A new offer has been created.</p>
        <p><strong>Name:</strong> {offer.name}</p>
        <p><strong>Code:</strong> {offer.code}</p>
        <p><strong>Discount:</strong> {offer.rate} ({offer.rate_type})</p>
        <p><strong>Active:</strong> {'Yes' if offer.is_active else 'No'}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"New Offer: {offer.name}", html_content)

    def send_offer_items_changed_notification(self, offer: EventOffer):
        html_content = f"""
        <h1>Offer Items Updated</h1>
        <p>The items associated with offer <strong>{offer.name}</strong> ({offer.code}) have been updated.</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Offer Items Updated: {offer.name}", html_content)

    def send_offer_disabled_notification(self, offer: EventOffer):
        html_content = f"""
        <h1>Offer Disabled</h1>
        <p>The offer <strong>{offer.name}</strong> ({offer.code}) has been disabled.</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Offer Disabled: {offer.name}", html_content)

    def send_product_added_notification(self, product: Product):
        html_content = f"""
        <h1>New Product Added</h1>
        <p>A new product has been added to the inventory.</p>
        <p><strong>Name:</strong> {product.name}</p>
        <p><strong>Price:</strong> ₹{product.selling_price}</p>
        <p><strong>Category ID:</strong> {product.category_id}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"New Product: {product.name}", html_content)

    def send_bulk_product_added_notification(self, products: List[Product]):
        items_html = "".join([
            f"<tr><td>{p.id}</td><td>{p.name}</td><td>{p.category_id}</td><td>₹{p.selling_price}</td></tr>"
            for p in products
        ])

        html_content = f"""
        <h1>Bulk Products Added</h1>
        <p>{len(products)} new products have been added to the inventory.</p>
        <table border="1" cellpadding="5" cellspacing="0">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Category ID</th>
                    <th>Price</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Bulk Products Added - {len(products)} items", html_content)

    def send_product_deleted_notification(self, product_id: int, product_name: str):
        html_content = f"""
        <h1>Product Deleted</h1>
        <p>A product has been removed from the system.</p>
        <p><strong>Product ID:</strong> {product_id}</p>
        <p><strong>Name:</strong> {product_name}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Product Deleted: {product_name}", html_content)

    def send_product_stock_updated_notification(self, product: Product, size: str, quantity_change: int):
        html_content = f"""
        <h1>Product Stock Updated</h1>
        <p>Stock has been updated for <strong>{product.name}</strong>.</p>
        <p><strong>Size:</strong> {size}</p>
        <p><strong>Quantity Change:</strong> {quantity_change}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Stock Update: {product.name}", html_content)

    def send_product_transfer_notification(self, products: List[Product], operation: str, destination_shop_id: int):
        product_names = ", ".join([p.name for p in products])
        html_content = f"""
        <h1>Products Transferred</h1>
        <p>Products have been {operation}ed.</p>
        <p><strong>Products:</strong> {product_names}</p>
        <p><strong>Destination Shop ID:</strong> {destination_shop_id}</p>
        """
        if settings.ADMIN_EMAIL:
            self._send_email(settings.ADMIN_EMAIL, f"Products {operation.capitalize()}ed", html_content)

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

        self._send_email(purchase.vendor.email, f"Purchase Confirmation #{purchase.id}", html_content)

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

        self._send_email(settings.MAIL_FROM, f"End of Day Summary - {day_summary.start_time.strftime('%Y-%m-%d')}", html_content)
