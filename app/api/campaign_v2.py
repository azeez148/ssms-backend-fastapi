from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.campaign import (
    CampaignV2Response, CampaignParticipationCreate, CampaignParticipationResponse,
    CampaignResultsResponse
)
from app.services.campaign import CampaignService

router = APIRouter()
campaign_service = CampaignService()

@router.get("", response_model=List[CampaignV2Response])
async def list_campaigns(status: Optional[str] = None, db: Session = Depends(get_db)):
    return campaign_service.get_campaigns_v2(db, status)

@router.get("/active", response_model=List[CampaignV2Response])
async def get_active_campaigns(db: Session = Depends(get_db)):
    return campaign_service.get_active_campaigns_v2(db)

@router.get("/my-participations", response_model=List[CampaignParticipationResponse])
async def get_my_participations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return campaign_service.get_my_participations_v2(db, str(current_user.id))

@router.get("/{id}", response_model=CampaignV2Response)
async def get_campaign_details(id: str, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign_v2_by_id(db, id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/{id}/participate", response_model=CampaignParticipationResponse)
async def participate_in_campaign(
    id: str,
    participation: CampaignParticipationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return campaign_service.participate_v2(db, id, str(current_user.id), participation.responses)
    except Exception as e:
        msg = str(e)
        if "Campaign not found" in msg:
            raise HTTPException(status_code=404, detail=msg)
        if "Already participated" in msg or "Campaign is not active" in msg or "Campaign has ended" in msg:
            raise HTTPException(status_code=403, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.get("/{id}/my-participation", response_model=Optional[CampaignParticipationResponse])
async def get_my_campaign_participation(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    participation = campaign_service.get_my_participation_v2(db, id, str(current_user.id))
    return participation

@router.get("/{id}/results", response_model=CampaignResultsResponse)
async def get_campaign_results(id: str, db: Session = Depends(get_db)):
    results = campaign_service.get_campaign_results_v2(db, id)
    if not results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return results
