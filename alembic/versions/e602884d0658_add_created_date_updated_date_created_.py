"""Add created_date, updated_date, created_by, updated_by to all tables

Revision ID: e602884d0658
Revises: 3ca337c806e3
Create Date: 2025-08-12 18:32:58.030265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e602884d0658'
down_revision = '3ca337c806e3'
branch_labels = None
depends_on = None

TABLES = [
    'attributes', 'categories', 'customers', 'days', 'delivery_types',
    'event_offers', 'expenses', 'payment_types', 'product_sizes', 'products',
    'purchase_items', 'purchases', 'sale_items', 'sales', 'shops', 'vendors'
]

def upgrade() -> None:
    for table_name in TABLES:
        op.add_column(table_name, sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
        op.add_column(table_name, sa.Column('updated_date', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True))
        op.add_column(table_name, sa.Column('created_by', sa.String(), nullable=True))
        op.add_column(table_name, sa.Column('updated_by', sa.String(), nullable=True))


def downgrade() -> None:
    for table_name in TABLES:
        op.drop_column(table_name, 'updated_by')
        op.drop_column(table_name, 'created_by')
        op.drop_column(table_name, 'updated_date')
        op.drop_column(table_name, 'created_date')
