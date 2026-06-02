from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any, Dict
from datetime import datetime
from app.schemas.base import BaseSchema
from app.models.campaign import (
    CampaignStatus, SubmissionStatus, WinnerType, CommunicationChannel, RecipientType,
    CampaignTypeV2, CampaignStatusV2, FieldType, ParticipationStatus
)

# V2 Schemas
class CampaignFieldSchema(BaseModel):
    id: str
    label: str
    type: FieldType
    required: bool = True
    options: Optional[List[str]] = None
    order: Optional[int] = 0

    class Config:
        from_attributes = True

class CampaignV2Response(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    type: CampaignTypeV2
    status: CampaignStatusV2
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    image_url: Optional[str] = Field(None, alias="imageUrl")
    rules: Optional[List[str]] = None
    terms_and_conditions: Optional[str] = Field(None, alias="termsAndConditions")
    fields: List[CampaignFieldSchema]
    winners: Optional[List[str]] = None
    results_summary: Optional[str] = Field(None, alias="resultsSummary")
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata", validation_alias="meta_data")
    participation_count: Optional[int] = Field(0, alias="participationCount")
    submission_count: Optional[int] = Field(0, alias="submissionCount")
    created_by: Optional[str] = Field(None, alias="createdBy")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignQuestionV2(BaseModel):
    type: FieldType
    label: str
    options: Optional[List[str]] = None
    required: bool = True
    order: Optional[int] = 0

class CreateCampaignRequestV2(BaseModel):
    title: str
    description: str
    type: CampaignTypeV2
    status: CampaignStatusV2
    starts_at: datetime = Field(..., alias="starts_at")
    ends_at: datetime = Field(..., alias="ends_at")
    metadata: Optional[Dict[str, Any]] = None
    questions: Optional[List[CampaignQuestionV2]] = None

    class Config:
        populate_by_name = True

class UpdateCampaignRequestV2(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[CampaignTypeV2] = None
    status: Optional[CampaignStatusV2] = None
    starts_at: Optional[datetime] = Field(None, alias="starts_at")
    ends_at: Optional[datetime] = Field(None, alias="ends_at")
    metadata: Optional[Dict[str, Any]] = None
    questions: Optional[List[CampaignQuestionV2]] = None

    class Config:
        populate_by_name = True

class PatchCampaignRequestV2(BaseModel):
    status: Optional[CampaignStatusV2] = None
    starts_at: Optional[datetime] = Field(None, alias="starts_at")
    ends_at: Optional[datetime] = Field(None, alias="ends_at")
    force: Optional[bool] = False

    class Config:
        populate_by_name = True

class CampaignListResponseV2(BaseModel):
    items: List[CampaignV2Response]
    page: int
    per_page: int = Field(..., alias="per_page")
    total: int

    class Config:
        populate_by_name = True

class CampaignParticipationCreate(BaseModel):
    responses: Dict[str, Any]

class CampaignParticipationResponse(BaseModel):
    id: str
    campaign_id: str = Field(..., alias="campaignId")
    user_id: str = Field(..., alias="userId")
    participation_date: datetime = Field(..., alias="participationDate")
    responses: Dict[str, Any]
    status: str

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignResultsV2(BaseModel):
    campaign_id: str = Field(..., alias="campaign_id")
    total_participations: int = Field(..., alias="total_participations")
    responses: Dict[str, Dict[str, int]]
    from_date: Optional[str] = Field(None, alias="from")
    to_date: Optional[str] = Field(None, alias="to")

    class Config:
        populate_by_name = True

class CampaignResultsResponse(BaseModel):
    winners: List[str]
    results_summary: Optional[str] = Field(None, alias="resultsSummary")

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignStatsV2(BaseModel):
    totalCampaigns: int
    activeCampaigns: int
    draftCampaigns: int
    totalParticipations: int
    completionRate: float

    class Config:
        populate_by_name = True

class BulkActionRequestV2(BaseModel):
    ids: List[str]
    action: str # 'publish' | 'unpublish' | 'delete' | 'pause'
    force: Optional[bool] = False

class BulkActionResponseV2(BaseModel):
    success: List[str]
    failed: List[Dict[str, str]] # [{id: string, error: string}]

# V1 Schemas
class CampaignQuestionBase(BaseModel):
    question_text: str = Field(..., alias="questionText")
    question_type: Optional[str] = Field(None, alias="questionType")
    options: Optional[List[str]] = None
    is_required: bool = Field(True, alias="isRequired")
    order: Optional[int] = None

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignQuestionCreate(CampaignQuestionBase):
    pass

class CampaignQuestionResponse(CampaignQuestionBase):
    id: int
    campaign_id: int = Field(..., alias="campaignId")

class CampaignParticipantBase(BaseModel):
    participant_name: Optional[str] = Field(None, alias="participantName")
    email: Optional[str] = None
    phone: Optional[str] = None
    submission_status: SubmissionStatus = Field(SubmissionStatus.NOT_STARTED, alias="submissionStatus")
    is_verified: bool = Field(False, alias="isVerified")

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignParticipantResponse(CampaignParticipantBase):
    id: int
    campaign_id: int = Field(..., alias="campaignId")
    joined_on: Optional[datetime] = Field(None, alias="joinedOn")

class CampaignSubmission(BaseModel):
    participant_id: int = Field(..., alias="participantId")

class CampaignWinnerBase(BaseModel):
    participant_id: Optional[int] = Field(None, alias="participantId")
    participant_name: Optional[str] = Field(None, alias="participantName")
    prize: Optional[str] = None
    winner_type: WinnerType = Field(..., alias="winnerType")
    selected_date: Optional[datetime] = Field(None, alias="selectedDate")
    selected_by: Optional[str] = Field(None, alias="selectedBy")

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignWinnerCreate(CampaignWinnerBase):
    pass

class CampaignWinnerResponse(CampaignWinnerBase):
    id: int
    campaign_id: int = Field(..., alias="campaignId")

class CampaignCommunicationBase(BaseModel):
    channel: CommunicationChannel
    recipient_type: RecipientType = Field(..., alias="recipientType")
    subject: Optional[str] = None
    message: str
    sent_by: Optional[str] = Field(None, alias="sentBy")

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignCommunicationCreate(CampaignCommunicationBase):
    pass

class CampaignCommunicationResponse(CampaignCommunicationBase):
    id: int
    campaign_id: int = Field(..., alias="campaignId")
    sent_at: Optional[datetime] = Field(None, alias="sentAt")
    recipient_count: Optional[int] = Field(None, alias="recipientCount")

class CampaignBase(BaseModel):
    name: str
    slug: Optional[str] = None
    type: Optional[str] = None
    short_description: Optional[str] = Field(None, alias="shortDescription")
    detailed_description: Optional[str] = Field(None, alias="detailedDescription")
    terms_and_conditions: Optional[str] = Field(None, alias="termsAndConditions")
    desktop_banner: Optional[str] = Field(None, alias="desktopBanner")
    mobile_banner: Optional[str] = Field(None, alias="mobileBanner")
    promotional_images: Optional[List[str]] = Field(default_factory=list, alias="promotionalImages")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    end_date: Optional[datetime] = Field(None, alias="endDate")
    registration_deadline: Optional[datetime] = Field(None, alias="registrationDeadline")
    submission_deadline: Optional[datetime] = Field(None, alias="submissionDeadline")
    status: CampaignStatus = CampaignStatus.DRAFT
    is_visible: bool = Field(True, alias="isVisible")
    participation_requirements: Optional[str] = Field(None, alias="participationRequirements")

    @model_validator(mode='after')
    def validate_dates(self) -> 'CampaignBase':
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("startDate must be before endDate")
        return self

    class Config:
        populate_by_name = True
        from_attributes = True

class CampaignCreate(CampaignBase):
    questions: Optional[List[CampaignQuestionCreate]] = None

class CampaignUpdate(CampaignBase):
    id: int
    name: Optional[str] = None
    slug: Optional[str] = None

class CampaignStatusUpdate(BaseModel):
    status: CampaignStatus

class CampaignResponse(CampaignBase, BaseSchema):
    id: int
    total_participants: int = Field(0, alias="totalParticipants")
    total_submissions: int = Field(0, alias="totalSubmissions")
    questions: Optional[List[CampaignQuestionResponse]] = None

class CampaignListResponse(BaseModel):
    items: List[CampaignResponse]
    total: int
    page: int
    size: int

    class Config:
        populate_by_name = True

class CampaignParticipantListResponse(BaseModel):
    items: List[CampaignParticipantResponse]
    total: int
    page: int
    size: int

    class Config:
        populate_by_name = True

class CampaignStats(BaseModel):
    total_campaigns: int = Field(..., alias="totalCampaigns")
    active_campaigns: int = Field(..., alias="activeCampaigns")
    total_participants: int = Field(..., alias="totalParticipants")
    total_submissions: int = Field(..., alias="totalSubmissions")
    winners_announced: int = Field(..., alias="winnersAnnounced")

    class Config:
        populate_by_name = True
