"""add campaign v2 tables

Revision ID: d2e3f4g5h6i7
Revises: bc21107894a0
Create Date: 2026-06-02 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2e3f4g5h6i7'
down_revision = 'bc21107894a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('campaigns_v2',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('survey', 'giveaway', 'discount', 'prediction', 'lucky_draw', name='campaigntypev2'), nullable=True),
    sa.Column('status', sa.Enum('draft', 'active', 'paused', 'ended', 'scheduled', 'closed', 'results_announced', name='campaignstatusv2'), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('rules', sa.JSON(), nullable=True),
    sa.Column('terms_and_conditions', sa.Text(), nullable=True),
    sa.Column('winners', sa.JSON(), nullable=True),
    sa.Column('results_summary', sa.Text(), nullable=True),
    sa.Column('meta_data', sa.JSON(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_v2_id'), 'campaigns_v2', ['id'], unique=False)

    op.create_table('campaign_fields',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('campaign_id', sa.String(), nullable=True),
    sa.Column('label', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('text', 'number', 'email', 'select', 'textarea', 'choice', name='fieldtype'), nullable=True),
    sa.Column('required', sa.Boolean(), nullable=True),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns_v2.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_fields_id'), 'campaign_fields', ['id'], unique=False)

    op.create_table('campaign_participations',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('campaign_id', sa.String(), nullable=True),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('participation_date', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('responses', sa.JSON(), nullable=True),
    sa.Column('status', sa.Enum('SUBMITTED', 'WINNER', 'PARTICIPATED', name='participationstatus'), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns_v2.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaign_participations_id'), 'campaign_participations', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_campaign_participations_id'), table_name='campaign_participations')
    op.drop_table('campaign_participations')
    op.drop_index(op.f('ix_campaign_fields_id'), table_name='campaign_fields')
    op.drop_table('campaign_fields')
    op.drop_index(op.f('ix_campaigns_v2_id'), table_name='campaigns_v2')
    op.drop_table('campaigns_v2')

    # Optional: Drop types if needed for Postgres
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        sa.Enum(name='campaigntypev2').drop(bind)
        sa.Enum(name='campaignstatusv2').drop(bind)
        sa.Enum(name='fieldtype').drop(bind)
        sa.Enum(name='participationstatus').drop(bind)
