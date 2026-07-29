"""add size_map to categories

Revision ID: b900a90f104b
Revises: 67170df16f2a
Create Date: 2026-03-06 10:32:04.033471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b900a90f104b'
down_revision = '67170df16f2a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('size_map', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('categories', 'size_map')
