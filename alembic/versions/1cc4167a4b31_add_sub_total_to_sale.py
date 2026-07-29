"""add sub_total to sale

Revision ID: 1cc4167a4b31
Revises: None
Create Date: 2025-08-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cc4167a4b31'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('sales', sa.Column('sub_total', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('sales', 'sub_total')
