"""Add category_discounts table

Revision ID: 99f18e9d4a3b
Revises: 8cbefaf72ebd
Create Date: 2026-02-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99f18e9d4a3b'
down_revision = '8cbefaf72ebd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'category_discounts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('discounted_price', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_id')
    )
    op.create_index(op.f('ix_category_discounts_id'), 'category_discounts', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_category_discounts_id'), table_name='category_discounts')
    op.drop_table('category_discounts')
