"""Add discount_type and discount_value to Offer model

Revision ID: 1a2b3c4d5e6f
Revises: aa17517ee8be
Create Date: 2025-07-31 02:36:48.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, None] = 'aa17517ee8be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('offers', sa.Column('discount_type', sa.String(), nullable=True))
    op.add_column('offers', sa.Column('discount_value', sa.Integer(), nullable=True))
    op.drop_column('offers', 'discount_percentage')


def downgrade() -> None:
    op.add_column('offers', sa.Column('discount_percentage', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('offers', 'discount_value')
    op.drop_column('offers', 'discount_type')
