import psycopg2
import os
from app.core import database

def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        dbname=database.POSTGRES_DB,
        user=database.POSTGRES_USER,
        password=database.POSTGRES_PASSWORD,
        host=database.POSTGRES_SERVER,
    )

def execute_sql_file(filename):
    """Execute SQL file contents."""
    conn = get_db_connection()
    cur = conn.cursor()

    with open(filename, 'r') as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()

def find_product_image(product_id):
    """
    Check for product image in images/products directory.
    Returns the relative URL if found, None otherwise.
    """
    image_dir = os.path.join('images', 'products', str(product_id))
    if not os.path.exists(image_dir):
        return None

    # Check for common image formats
    image_formats = ['.jpg', '.jpeg', '.png', '.avif', '.webp']
    for ext in image_formats:
        image_path = os.path.join(image_dir, f"{product_id}{ext}")
        if os.path.exists(image_path):
            # Return relative URL path for FastAPI static files
            return f"/images/products/{product_id}/{product_id}{ext}"
    
    # Check if there's any image file in the directory
    if os.path.exists(image_dir):
        files = os.listdir(image_dir)
        image_files = [f for f in files if any(f.lower().endswith(ext) for ext in image_formats)]
        if image_files:
            # Return the first found image
            return f"images/products/{product_id}/{image_files[0]}"
    
    return None

def update_product_images():
    """Update product image URLs in database."""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Get all products with null or empty image_url
        cur.execute("""
            SELECT id, name 
            FROM products 
            WHERE image_url IS NULL OR image_url = ''
        """)
        products = cur.fetchall()

        updated_count = 0
        for product_id, product_name in products:
            image_url = find_product_image(product_id)
            if image_url:
                cur.execute("""
                    UPDATE products 
                    SET image_url = %s 
                    WHERE id = %s
                """, (image_url, product_id))
                updated_count += 1
                print(f"Updated image URL for product {product_id}: {product_name}")

        conn.commit()
        print(f"\nUpdated {updated_count} products with image URLs")

    except Exception as e:
        print(f"Error updating product images: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def run_sql_migrations():
    print("Running SQL Update...")
    # execute_sql_file('products_new.sql')
    # print("SQL Migration completed!")
    
    print("\nChecking and updating product images...")
    update_product_images()

if __name__ == "__main__":
    run_sql_migrations()
    print("\nAll operations completed successfully!")
