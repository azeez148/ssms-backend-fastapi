"""Add variance and variance_reason to days table

Revision ID: a1b2c3d4e5f6
Revises: 99f18e9d4a3b
Create Date: 2025-02-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '99f18e9d4a3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('days', sa.Column('variance', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('days', sa.Column('variance_reason', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('days', 'variance_reason')
    op.drop_column('days', 'variance')
