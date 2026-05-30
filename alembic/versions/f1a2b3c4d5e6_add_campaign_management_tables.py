"""add_campaign_management_tables

Revision ID: f1a2b3c4d5e6
Revises: 67170df16f2a
Create Date: 2026-05-30 19:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = '67170df16f2a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('campaign_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('draft', 'active', 'paused', 'completed', 'cancelled', name='campaignstatus'), nullable=False),
        sa.Column('terms_and_conditions', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('participation_requirements', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_slug'), 'campaigns', ['slug'], unique=True)

    op.create_table(
        'campaign_media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('media_type', sa.String(length=50), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_media_id'), 'campaign_media', ['id'], unique=False)

    op.create_table(
        'campaign_forms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_forms_id'), 'campaign_forms', ['id'], unique=False)

    op.create_table(
        'campaign_form_fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('form_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(length=255), nullable=False),
        sa.Column('field_label', sa.String(length=255), nullable=False),
        sa.Column('field_type', sa.Enum('text', 'textarea', 'number', 'email', 'phone', 'select', 'multi_select', 'radio', 'checkbox', 'date', 'file', 'image', 'url', name='fieldtype'), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('placeholder', sa.String(length=255), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('validation_rules', sa.JSON(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['form_id'], ['campaign_forms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_form_fields_id'), 'campaign_form_fields', ['id'], unique=False)

    op.create_table(
        'campaign_deadlines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('deadline_type', sa.String(length=50), nullable=False),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_enforced', sa.Boolean(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_deadlines_id'), 'campaign_deadlines', ['id'], unique=False)

    op.create_table(
        'campaign_winner_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('strategy', sa.Enum('manual', 'random', 'daily', 'scheduled', 'final', name='winnerstrategy'), nullable=False),
        sa.Column('max_winners', sa.Integer(), nullable=True),
        sa.Column('schedule_config', sa.JSON(), nullable=True),
        sa.Column('criteria', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_winner_configs_id'), 'campaign_winner_configs', ['id'], unique=False)

    op.create_table(
        'campaign_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('whatsapp_number', sa.String(length=20), nullable=True),
        sa.Column('status', sa.Enum('registered', 'active', 'submitted', 'winner', 'disqualified', name='participationstatus'), nullable=False),
        sa.Column('participant_metadata', sa.JSON(), nullable=True),
        sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_participants_id'), 'campaign_participants', ['id'], unique=False)

    op.create_table(
        'campaign_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('form_id', sa.Integer(), nullable=True),
        sa.Column('response_data', sa.JSON(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['form_id'], ['campaign_forms.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['participant_id'], ['campaign_participants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_submissions_id'), 'campaign_submissions', ['id'], unique=False)

    op.create_table(
        'campaign_communications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.Enum('email', 'whatsapp', name='communicationchannel'), nullable=False),
        sa.Column('trigger', sa.Enum('registration', 'submission', 'winner_announcement', 'reminder', 'custom', name='communicationtrigger'), nullable=False),
        sa.Column('template_subject', sa.String(length=500), nullable=True),
        sa.Column('template_body', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_campaign_communications_id'), 'campaign_communications', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('campaign_communications')
    op.drop_table('campaign_submissions')
    op.drop_table('campaign_participants')
    op.drop_table('campaign_winner_configs')
    op.drop_table('campaign_deadlines')
    op.drop_table('campaign_form_fields')
    op.drop_table('campaign_forms')
    op.drop_table('campaign_media')
    op.drop_table('campaigns')
    op.execute("DROP TYPE IF EXISTS campaignstatus")
    op.execute("DROP TYPE IF EXISTS winnerstrategy")
    op.execute("DROP TYPE IF EXISTS fieldtype")
    op.execute("DROP TYPE IF EXISTS participationstatus")
    op.execute("DROP TYPE IF EXISTS communicationchannel")
    op.execute("DROP TYPE IF EXISTS communicationtrigger")
