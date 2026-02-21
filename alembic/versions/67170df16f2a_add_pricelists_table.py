"""Add pricelists table

Revision ID: 67170df16f2a
Revises: 03a3ae774e10
Create Date: 2026-02-21 10:16:15.913284

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67170df16f2a'
down_revision = '03a3ae774e10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pricelists',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('unit_price', sa.Integer(), nullable=True),
        sa.Column('selling_price', sa.Integer(), nullable=True),
        sa.Column('discounted_price', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_id')
    )
    op.create_index(op.f('ix_pricelists_id'), 'pricelists', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_pricelists_id'), table_name='pricelists')
    op.drop_table('pricelists')
