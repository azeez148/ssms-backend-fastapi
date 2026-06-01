"""add_performance_indexes_for_hot_queries

Revision ID: f7b3c5d9e2a1
Revises: e6590816b80c
Create Date: 2026-05-30 12:10:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f7b3c5d9e2a1"
down_revision = "e6590816b80c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Sales filters used by dashboard/report/day-management.
    op.create_index("ix_sales_status", "sales", ["status"], unique=False)
    op.create_index("ix_sales_shop_id", "sales", ["shop_id"], unique=False)
    op.create_index("ix_sales_date", "sales", ["date"], unique=False)
    op.create_index("ix_sales_status_shop_date", "sales", ["status", "shop_id", "date"], unique=False)

    # Sale item lookups and joins used in reporting and sale detail loading.
    op.create_index("ix_sale_items_sale_id", "sale_items", ["sale_id"], unique=False)
    op.create_index("ix_sale_items_product_id", "sale_items", ["product_id"], unique=False)

    # Product size lookups used in stock updates and availability checks.
    op.create_index("ix_product_sizes_product_id", "product_sizes", ["product_id"], unique=False)
    op.create_index("ix_product_sizes_product_id_size", "product_sizes", ["product_id", "size"], unique=False)

    # Day lookups by shop and start_time range/date.
    op.create_index("ix_days_shop_start_time", "days", ["shop_id", "start_time"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_days_shop_start_time", table_name="days")

    op.drop_index("ix_product_sizes_product_id_size", table_name="product_sizes")
    op.drop_index("ix_product_sizes_product_id", table_name="product_sizes")

    op.drop_index("ix_sale_items_product_id", table_name="sale_items")
    op.drop_index("ix_sale_items_sale_id", table_name="sale_items")

    op.drop_index("ix_sales_status_shop_date", table_name="sales")
    op.drop_index("ix_sales_date", table_name="sales")
    op.drop_index("ix_sales_shop_id", table_name="sales")
    op.drop_index("ix_sales_status", table_name="sales")
