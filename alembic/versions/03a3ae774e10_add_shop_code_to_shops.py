"""add shop_code to shops

Revision ID: 03a3ae774e10
Revises: c1d2e3f4g5h6
Create Date: 2026-02-21 06:27:13.633240

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03a3ae774e10'
down_revision = 'c1d2e3f4g5h6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('shops', sa.Column('shop_code', sa.String(), nullable=True))
    op.create_index(op.f('ix_shops_shop_code'), 'shops', ['shop_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_shops_shop_code'), table_name='shops')
    op.drop_column('shops', 'shop_code')
