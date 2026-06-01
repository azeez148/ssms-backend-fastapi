"""Add campaign module tables

Revision ID: bc21107894a0
Revises: e6590816b80c
Create Date: 2026-06-01 13:20:41.638540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc21107894a0'
down_revision = 'e6590816b80c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('campaigns',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('short_description', sa.String(length=160), nullable=True),
    sa.Column('detailed_description', sa.Text(), nullable=True),
    sa.Column('terms_and_conditions', sa.Text(), nullable=True),
    sa.Column('desktop_banner', sa.String(), nullable=True),
    sa.Column('mobile_banner', sa.String(), nullable=True),
    sa.Column('promotional_images', sa.JSON(), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('registration_deadline', sa.DateTime(), nullable=True),
    sa.Column('submission_deadline', sa.DateTime(), nullable=True),
    sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'INACTIVE', 'CLOSED', 'COMPLETED', name='campaignstatus'), nullable=True),
    sa.Column('is_visible', sa.Boolean(), nullable=True),
    sa.Column('participation_requirements', sa.Text(), nullable=True),
    sa.Column('total_participants', sa.Integer(), nullable=True),
    sa.Column('total_submissions', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_slug'), 'campaigns', ['slug'], unique=True)

    op.create_table('campaign_communications',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=True),
    sa.Column('channel', sa.Enum('EMAIL', 'WHATSAPP', name='communicationchannel'), nullable=True),
    sa.Column('recipient_type', sa.Enum('ALL', 'INDIVIDUAL', name='recipienttype'), nullable=True),
    sa.Column('subject', sa.String(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('sent_by', sa.String(), nullable=True),
    sa.Column('recipient_count', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('campaign_participants',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=True),
    sa.Column('participant_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('joined_on', sa.DateTime(), nullable=True),
    sa.Column('submission_status', sa.Enum('SUBMITTED', 'PENDING', 'NOT_STARTED', name='submissionstatus'), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('campaign_questions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=True),
    sa.Column('question_text', sa.String(), nullable=False),
    sa.Column('question_type', sa.String(), nullable=True),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('is_required', sa.Boolean(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('campaign_winners',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=True),
    sa.Column('participant_id', sa.Integer(), nullable=True),
    sa.Column('participant_name', sa.String(), nullable=True),
    sa.Column('prize', sa.String(), nullable=True),
    sa.Column('winner_type', sa.Enum('DAILY', 'WEEKLY', 'MONTHLY', 'FINAL', 'CUSTOM', name='winnertype'), nullable=True),
    sa.Column('selected_date', sa.DateTime(), nullable=True),
    sa.Column('selected_by', sa.String(), nullable=True),
    sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.ForeignKeyConstraint(['participant_id'], ['campaign_participants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('campaign_winners')
    op.drop_table('campaign_questions')
    op.drop_table('campaign_participants')
    op.drop_table('campaign_communications')
    op.drop_index(op.f('ix_campaigns_slug'), table_name='campaigns')
    op.drop_table('campaigns')
