"""Add Offer model and offer_products association table

Revision ID: aa17517ee8be
Revises: 627526f6db24
Create Date: 2025-07-31 02:22:21.321869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa17517ee8be'
down_revision: Union[str, None] = '627526f6db24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('offers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('discount_percentage', sa.Integer(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offers_id'), 'offers', ['id'], unique=False)
    op.create_index(op.f('ix_offers_name'), 'offers', ['name'], unique=False)
    op.create_table('offer_products',
    sa.Column('offer_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['offer_id'], ['offers.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('offer_id', 'product_id')
    )


def downgrade() -> None:
    op.drop_table('offer_products')
    op.drop_index(op.f('ix_offers_name'), table_name='offers')
    op.drop_index(op.f('ix_offers_id'), table_name='offers')
    op.drop_table('offers')
