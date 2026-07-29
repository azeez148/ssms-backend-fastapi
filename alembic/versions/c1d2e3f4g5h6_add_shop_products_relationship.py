"""Add shop_products relationship and migrate existing products

Revision ID: c1d2e3f4g5h6
Revises: b1c2d3e4f5g6
Create Date: 2025-02-20 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1d2e3f4g5h6'
down_revision = 'b1c2d3e4f5g6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create shop_products association table if it doesn't exist
    # Using checkfirst=True in standard SQL but Alembic uses op commands
    op.create_table(
        'shop_products',
        sa.Column('shop_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['shop_id'], ['shops.id'], ),
        sa.PrimaryKeyConstraint('shop_id', 'product_id')
    )

    # 2. Ensure Shop ID 1 exists
    # We use raw SQL for this to be safe and handle existing/missing shop 1
    op.execute("""
        INSERT INTO shops (id, name, "addressLine1", "addressLine2", city, state, country, zipcode, "mobileNumber", email, created_by, updated_by)
        SELECT 1, 'Default Shop', 'Main St', '', 'Default City', 'Default State', 'Default Country', '000000', '0000000000', 'default@shop.com', 'system', 'system'
        WHERE NOT EXISTS (SELECT 1 FROM shops WHERE id = 1)
    """)

    # 3. Associate all existing products with Shop ID 1
    op.execute("""
        INSERT INTO shop_products (shop_id, product_id)
        SELECT 1, id FROM products
        WHERE id NOT IN (SELECT product_id FROM shop_products WHERE shop_id = 1)
    """)


def downgrade() -> None:
    op.drop_table('shop_products')
