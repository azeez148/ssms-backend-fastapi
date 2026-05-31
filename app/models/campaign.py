from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class CampaignStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    CLOSED = "Closed"
    COMPLETED = "Completed"

class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "Submitted"
    PENDING = "Pending"
    NOT_STARTED = "Not Started"

class WinnerType(str, enum.Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    FINAL = "Final"
    CUSTOM = "Custom"

class CommunicationChannel(str, enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"

class RecipientType(str, enum.Enum):
    ALL = "all"
    INDIVIDUAL = "individual"

class Campaign(BaseModel):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    type = Column(String)
    short_description = Column(String(160))
    detailed_description = Column(Text)
    terms_and_conditions = Column(Text)
    desktop_banner = Column(String)
    mobile_banner = Column(String)
    promotional_images = Column(JSON)  # Array of URLs
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    registration_deadline = Column(DateTime)
    submission_deadline = Column(DateTime)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    is_visible = Column(Boolean, default=True)
    participation_requirements = Column(Text)
    total_participants = Column(Integer, default=0)
    total_submissions = Column(Integer, default=0)

    questions = relationship("CampaignQuestion", back_populates="campaign", cascade="all, delete-orphan")
    participants = relationship("CampaignParticipant", back_populates="campaign", cascade="all, delete-orphan")
    winners = relationship("CampaignWinner", back_populates="campaign", cascade="all, delete-orphan")
    communications = relationship("CampaignCommunication", back_populates="campaign", cascade="all, delete-orphan")

class CampaignQuestion(BaseModel):
    __tablename__ = "campaign_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    question_text = Column(String, nullable=False)
    question_type = Column(String)
    options = Column(JSON)  # Array of strings
    is_required = Column(Boolean, default=True)
    order = Column(Integer)

    campaign = relationship("Campaign", back_populates="questions")

class CampaignParticipant(BaseModel):
    __tablename__ = "campaign_participants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    participant_name = Column(String)
    email = Column(String)
    phone = Column(String)
    joined_on = Column(DateTime, server_default=None) # Will be set in service
    submission_status = Column(Enum(SubmissionStatus), default=SubmissionStatus.NOT_STARTED)
    is_verified = Column(Boolean, default=False)

    campaign = relationship("Campaign", back_populates="participants")
    winner_entry = relationship("CampaignWinner", back_populates="participant", uselist=False)

class CampaignWinner(BaseModel):
    __tablename__ = "campaign_winners"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    participant_id = Column(Integer, ForeignKey("campaign_participants.id"), nullable=True)
    participant_name = Column(String)
    prize = Column(String)
    winner_type = Column(Enum(WinnerType))
    selected_date = Column(DateTime)
    selected_by = Column(String)

    campaign = relationship("Campaign", back_populates="winners")
    participant = relationship("CampaignParticipant", back_populates="winner_entry")

class CampaignCommunication(BaseModel):
    __tablename__ = "campaign_communications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    channel = Column(Enum(CommunicationChannel))
    recipient_type = Column(Enum(RecipientType))
    subject = Column(String, nullable=True)
    message = Column(Text)
    sent_at = Column(DateTime)
    sent_by = Column(String)
    recipient_count = Column(Integer)

    campaign = relationship("Campaign", back_populates="communications")
