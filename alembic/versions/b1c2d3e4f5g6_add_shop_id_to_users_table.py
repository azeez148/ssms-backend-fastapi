"""Add shop_id to users table

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2025-02-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5g6'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add shop_id column to users table
    op.add_column('users', sa.Column('shop_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(None, 'users', 'shops', ['shop_id'], ['id'])
    
    # Update existing staff users to shop_id = 1
    op.execute("UPDATE users SET shop_id = 1 WHERE role = 'staff' AND shop_id IS NULL")


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint(None, 'users', type_='foreignkey')
    
    # Drop column
    op.drop_column('users', 'shop_id')
