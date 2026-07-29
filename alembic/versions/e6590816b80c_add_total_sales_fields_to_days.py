"""add_total_sales_fields_to_days

Revision ID: e6590816b80c
Revises: b900a90f104b
Create Date: 2026-05-11 10:58:18.490966

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e6590816b80c'
down_revision = 'b900a90f104b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('days', sa.Column('total_sales', sa.Float(), nullable=True))
    op.add_column('days', sa.Column('total_cash_sales', sa.Float(), nullable=True))
    op.add_column('days', sa.Column('total_account_sales', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('days', 'total_account_sales')
    op.drop_column('days', 'total_cash_sales')
    op.drop_column('days', 'total_sales')
