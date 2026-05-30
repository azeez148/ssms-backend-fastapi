from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.models.base import BaseModel


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WinnerStrategy(str, enum.Enum):
    MANUAL = "manual"
    RANDOM = "random"
    DAILY = "daily"
    SCHEDULED = "scheduled"
    FINAL = "final"


class FieldType(str, enum.Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE = "date"
    FILE = "file"
    IMAGE = "image"
    URL = "url"


class ParticipationStatus(str, enum.Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    SUBMITTED = "submitted"
    WINNER = "winner"
    DISQUALIFIED = "disqualified"


class CommunicationChannel(str, enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class CommunicationTrigger(str, enum.Enum):
    REGISTRATION = "registration"
    SUBMISSION = "submission"
    WINNER_ANNOUNCEMENT = "winner_announcement"
    REMINDER = "reminder"
    CUSTOM = "custom"


class Campaign(BaseModel):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    campaign_type = Column(String(100), nullable=False)
    status = Column(SAEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    terms_and_conditions = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    participation_requirements = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    media = relationship("CampaignMedia", back_populates="campaign", cascade="all, delete-orphan")
    forms = relationship("CampaignForm", back_populates="campaign", cascade="all, delete-orphan")
    deadlines = relationship("CampaignDeadline", back_populates="campaign", cascade="all, delete-orphan")
    winner_configs = relationship("CampaignWinnerConfig", back_populates="campaign", cascade="all, delete-orphan")
    participants = relationship("CampaignParticipant", back_populates="campaign", cascade="all, delete-orphan")
    communications = relationship("CampaignCommunication", back_populates="campaign", cascade="all, delete-orphan")


class CampaignMedia(BaseModel):
    __tablename__ = "campaign_media"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    media_type = Column(String(50), nullable=False)  # image, video, document
    url = Column(String(500), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)

    campaign = relationship("Campaign", back_populates="media")


class CampaignForm(BaseModel):
    __tablename__ = "campaign_forms"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    campaign = relationship("Campaign", back_populates="forms")
    fields = relationship("CampaignFormField", back_populates="form", cascade="all, delete-orphan")


class CampaignFormField(BaseModel):
    __tablename__ = "campaign_form_fields"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("campaign_forms.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(255), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_type = Column(SAEnum(FieldType), nullable=False)
    is_required = Column(Boolean, default=False)
    placeholder = Column(String(255), nullable=True)
    options = Column(JSON, nullable=True)  # For select, radio, checkbox types
    validation_rules = Column(JSON, nullable=True)
    sort_order = Column(Integer, default=0)

    form = relationship("CampaignForm", back_populates="fields")


class CampaignDeadline(BaseModel):
    __tablename__ = "campaign_deadlines"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    deadline_type = Column(String(50), nullable=False)  # registration, participation, submission, result_publication
    starts_at = Column(DateTime(timezone=True), nullable=True)
    ends_at = Column(DateTime(timezone=True), nullable=False)
    is_enforced = Column(Boolean, default=True)

    campaign = relationship("Campaign", back_populates="deadlines")


class CampaignWinnerConfig(BaseModel):
    __tablename__ = "campaign_winner_configs"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    strategy = Column(SAEnum(WinnerStrategy), nullable=False)
    max_winners = Column(Integer, default=1)
    schedule_config = Column(JSON, nullable=True)  # For scheduled/daily strategies
    criteria = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    campaign = relationship("Campaign", back_populates="winner_configs")


class CampaignParticipant(BaseModel):
    __tablename__ = "campaign_participants"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    whatsapp_number = Column(String(20), nullable=True)
    status = Column(SAEnum(ParticipationStatus), default=ParticipationStatus.REGISTERED, nullable=False)
    participant_metadata = Column(JSON, nullable=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    campaign = relationship("Campaign", back_populates="participants")
    submissions = relationship("CampaignSubmission", back_populates="participant", cascade="all, delete-orphan")


class CampaignSubmission(BaseModel):
    __tablename__ = "campaign_submissions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(Integer, ForeignKey("campaign_participants.id", ondelete="CASCADE"), nullable=False)
    form_id = Column(Integer, ForeignKey("campaign_forms.id", ondelete="SET NULL"), nullable=True)
    response_data = Column(JSON, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    participant = relationship("CampaignParticipant", back_populates="submissions")


class CampaignCommunication(BaseModel):
    __tablename__ = "campaign_communications"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    channel = Column(SAEnum(CommunicationChannel), nullable=False)
    trigger = Column(SAEnum(CommunicationTrigger), nullable=False)
    template_subject = Column(String(500), nullable=True)
    template_body = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)

    campaign = relationship("Campaign", back_populates="communications")
