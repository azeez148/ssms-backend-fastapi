from sqlalchemy.orm import Session
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.product import Product
from app.core.config import settings
import emails
import pywhatkit

class WhatsAppNotificationService:
    def send_sale_notification(self, db: Session, sale: Sale):
        if not sale.customer or not sale.customer.mobile:
            return

        try:
            # Constructing the message with sale details
            message = f"Hi {sale.customer.name}, your sale with ID #{sale.id} has been confirmed.\n\n"
            message += "Here are the details of your order:\n"

            items_details = []
            for item in sale.sale_items:
                items_details.append(
                    f"- {item.product_name} (Size: {item.size}, Quantity: {item.quantity}, Price: {item.sale_price})"
                )

            message += "\n".join(items_details)
            message += f"\n\nTotal amount: {sale.total_price}"

            # Add shop's social media and website links
            if sale.shop:
                message += "\n\nFollow us for updates and offers:"
                if sale.shop.instagram_link:
                    message += f"\nInstagram: {sale.shop.instagram_link}"
                if sale.shop.whatsapp_group_link:
                    message += f"\nWhatsApp Group: {sale.shop.whatsapp_group_link}"
                if sale.shop.website_link:
                    message += f"\nWebsite: {sale.shop.website_link}"

            # Get the image of the first product
            image_path = None
            if sale.sale_items:
                first_item = sale.sale_items[0]
                product = db.query(Product).filter(Product.id == first_item.product_id).first()
                if product and product.image_url:
                    image_path = product.image_url

            # Send WhatsApp message
            if image_path:
                pywhatkit.sendwhats_image(
                    receiver=sale.customer.mobile,
                    img_path=image_path,
                    caption=message
                )
            else:
                pywhatkit.sendwhatmsg_instantly(
                    phone_no=sale.customer.mobile,
                    message=message
                )
        except Exception as e:
            print(f"Failed to send WhatsApp message to {sale.customer.mobile}: {e}")

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
