from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# Enums
class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WinnerStrategyEnum(str, Enum):
    MANUAL = "manual"
    RANDOM = "random"
    DAILY = "daily"
    SCHEDULED = "scheduled"
    FINAL = "final"


class FieldTypeEnum(str, Enum):
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


class ParticipationStatusEnum(str, Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    SUBMITTED = "submitted"
    WINNER = "winner"
    DISQUALIFIED = "disqualified"


class CommunicationChannelEnum(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class CommunicationTriggerEnum(str, Enum):
    REGISTRATION = "registration"
    SUBMISSION = "submission"
    WINNER_ANNOUNCEMENT = "winner_announcement"
    REMINDER = "reminder"
    CUSTOM = "custom"


# --- Media Schemas ---
class CampaignMediaBase(BaseModel):
    media_type: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class CampaignMediaCreate(CampaignMediaBase):
    pass


class CampaignMediaResponse(CampaignMediaBase):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


# --- Form Field Schemas ---
class CampaignFormFieldBase(BaseModel):
    field_name: str
    field_label: str
    field_type: FieldTypeEnum
    is_required: bool = False
    placeholder: Optional[str] = None
    options: Optional[Any] = None
    validation_rules: Optional[Any] = None
    sort_order: int = 0


class CampaignFormFieldCreate(CampaignFormFieldBase):
    pass


class CampaignFormFieldResponse(CampaignFormFieldBase):
    id: int
    form_id: int

    class Config:
        from_attributes = True


# --- Form Schemas ---
class CampaignFormBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_required: bool = True
    sort_order: int = 0


class CampaignFormCreate(CampaignFormBase):
    fields: List[CampaignFormFieldCreate] = []


class CampaignFormResponse(CampaignFormBase):
    id: int
    campaign_id: int
    fields: List[CampaignFormFieldResponse] = []

    class Config:
        from_attributes = True


# --- Deadline Schemas ---
class CampaignDeadlineBase(BaseModel):
    deadline_type: str
    starts_at: Optional[datetime] = None
    ends_at: datetime
    is_enforced: bool = True


class CampaignDeadlineCreate(CampaignDeadlineBase):
    pass


class CampaignDeadlineResponse(CampaignDeadlineBase):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


# --- Winner Config Schemas ---
class CampaignWinnerConfigBase(BaseModel):
    strategy: WinnerStrategyEnum
    max_winners: int = 1
    schedule_config: Optional[Any] = None
    criteria: Optional[Any] = None
    is_active: bool = True


class CampaignWinnerConfigCreate(CampaignWinnerConfigBase):
    pass


class CampaignWinnerConfigResponse(CampaignWinnerConfigBase):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


# --- Communication Schemas ---
class CampaignCommunicationBase(BaseModel):
    channel: CommunicationChannelEnum
    trigger: CommunicationTriggerEnum
    template_subject: Optional[str] = None
    template_body: str
    is_active: bool = True


class CampaignCommunicationCreate(CampaignCommunicationBase):
    pass


class CampaignCommunicationResponse(CampaignCommunicationBase):
    id: int
    campaign_id: int

    class Config:
        from_attributes = True


# --- Participant Schemas ---
class CampaignParticipantBase(BaseModel):
    name: str
    email: Optional[str] = None
    whatsapp_number: Optional[str] = None
    participant_metadata: Optional[Any] = None


class CampaignParticipantCreate(CampaignParticipantBase):
    pass


class CampaignParticipantResponse(CampaignParticipantBase):
    id: int
    campaign_id: int
    status: ParticipationStatusEnum
    registered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Submission Schemas ---
class CampaignSubmissionBase(BaseModel):
    form_id: Optional[int] = None
    response_data: Any


class CampaignSubmissionCreate(CampaignSubmissionBase):
    pass


class CampaignSubmissionResponse(CampaignSubmissionBase):
    id: int
    campaign_id: int
    participant_id: int
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Campaign Schemas ---
class CampaignBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    campaign_type: str
    terms_and_conditions: Optional[str] = None
    metadata_json: Optional[Any] = None
    participation_requirements: Optional[Any] = None
    is_active: bool = True


class CampaignCreate(CampaignBase):
    status: CampaignStatusEnum = CampaignStatusEnum.DRAFT
    media: List[CampaignMediaCreate] = []
    forms: List[CampaignFormCreate] = []
    deadlines: List[CampaignDeadlineCreate] = []
    winner_configs: List[CampaignWinnerConfigCreate] = []
    communications: List[CampaignCommunicationCreate] = []


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    campaign_type: Optional[str] = None
    status: Optional[CampaignStatusEnum] = None
    terms_and_conditions: Optional[str] = None
    metadata_json: Optional[Any] = None
    participation_requirements: Optional[Any] = None
    is_active: Optional[bool] = None


class CampaignResponse(CampaignBase):
    id: int
    status: CampaignStatusEnum
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignDetailResponse(CampaignResponse):
    media: List[CampaignMediaResponse] = []
    forms: List[CampaignFormResponse] = []
    deadlines: List[CampaignDeadlineResponse] = []
    winner_configs: List[CampaignWinnerConfigResponse] = []
    communications: List[CampaignCommunicationResponse] = []

    class Config:
        from_attributes = True


# --- Campaign Results ---
class CampaignResultsResponse(BaseModel):
    campaign_id: int
    campaign_name: str
    winners: List[CampaignParticipantResponse] = []
    total_participants: int
    total_submissions: int
