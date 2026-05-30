from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignDetailResponse,
    CampaignMediaCreate, CampaignMediaResponse,
    CampaignFormCreate, CampaignFormResponse,
    CampaignDeadlineCreate, CampaignDeadlineResponse,
    CampaignWinnerConfigCreate, CampaignWinnerConfigResponse,
    CampaignParticipantCreate, CampaignParticipantResponse,
    CampaignSubmissionCreate, CampaignSubmissionResponse,
    CampaignCommunicationCreate, CampaignCommunicationResponse,
    CampaignResultsResponse,
)
from app.services.campaign import CampaignService

router = APIRouter()
campaign_service = CampaignService()


# --- Campaign CRUD ---

@router.post("/", response_model=CampaignDetailResponse)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    return campaign_service.create_campaign(db, campaign)


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return campaign_service.get_all_campaigns(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[CampaignResponse])
async def list_active_campaigns(db: Session = Depends(get_db)):
    return campaign_service.get_active_campaigns(db)


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/slug/{slug}", response_model=CampaignDetailResponse)
async def get_campaign_by_slug(slug: str, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign_by_slug(db, slug)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: int, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    updated = campaign_service.update_campaign(db, campaign_id, campaign)
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    deleted = campaign_service.delete_campaign(db, campaign_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted successfully"}


# --- Media ---

@router.post("/{campaign_id}/media", response_model=CampaignMediaResponse)
async def add_media(campaign_id: int, media: CampaignMediaCreate, db: Session = Depends(get_db)):
    result = campaign_service.add_media(db, campaign_id, media)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


@router.delete("/media/{media_id}")
async def delete_media(media_id: int, db: Session = Depends(get_db)):
    deleted = campaign_service.delete_media(db, media_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Media not found")
    return {"message": "Media deleted successfully"}


# --- Forms ---

@router.post("/{campaign_id}/forms", response_model=CampaignFormResponse)
async def add_form(campaign_id: int, form: CampaignFormCreate, db: Session = Depends(get_db)):
    result = campaign_service.add_form(db, campaign_id, form)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


@router.delete("/forms/{form_id}")
async def delete_form(form_id: int, db: Session = Depends(get_db)):
    deleted = campaign_service.delete_form(db, form_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Form not found")
    return {"message": "Form deleted successfully"}


# --- Deadlines ---

@router.post("/{campaign_id}/deadlines", response_model=CampaignDeadlineResponse)
async def add_deadline(campaign_id: int, deadline: CampaignDeadlineCreate, db: Session = Depends(get_db)):
    result = campaign_service.add_deadline(db, campaign_id, deadline)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


# --- Winner Config ---

@router.post("/{campaign_id}/winner-configs", response_model=CampaignWinnerConfigResponse)
async def add_winner_config(
    campaign_id: int, config: CampaignWinnerConfigCreate, db: Session = Depends(get_db)
):
    result = campaign_service.add_winner_config(db, campaign_id, config)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


# --- Participants ---

@router.post("/{campaign_id}/participants", response_model=CampaignParticipantResponse)
async def register_participant(
    campaign_id: int, participant: CampaignParticipantCreate, db: Session = Depends(get_db)
):
    result = campaign_service.register_participant(db, campaign_id, participant)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Registration failed. Campaign not found, deadline passed, or requirements not met.",
        )
    return result


@router.get("/{campaign_id}/participants", response_model=List[CampaignParticipantResponse])
async def list_participants(campaign_id: int, db: Session = Depends(get_db)):
    return campaign_service.get_campaign_participants(db, campaign_id)


# --- Submissions ---

@router.post("/{campaign_id}/participants/{participant_id}/submissions", response_model=CampaignSubmissionResponse)
async def submit_response(
    campaign_id: int,
    participant_id: int,
    submission: CampaignSubmissionCreate,
    db: Session = Depends(get_db),
):
    result = campaign_service.submit_response(db, campaign_id, participant_id, submission)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Submission failed. Deadline passed or participant not found.",
        )
    return result


@router.get("/participants/{participant_id}/submissions", response_model=List[CampaignSubmissionResponse])
async def get_participant_submissions(participant_id: int, db: Session = Depends(get_db)):
    return campaign_service.get_participant_submissions(db, participant_id)


# --- Results ---

@router.get("/{campaign_id}/results", response_model=CampaignResultsResponse)
async def get_campaign_results(campaign_id: int, db: Session = Depends(get_db)):
    results = campaign_service.get_campaign_results(db, campaign_id)
    if not results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return results


@router.post("/{campaign_id}/winners")
async def select_winners(campaign_id: int, participant_ids: List[int], db: Session = Depends(get_db)):
    winners = campaign_service.select_winners_manual(db, campaign_id, participant_ids)
    if not winners:
        raise HTTPException(status_code=400, detail="No valid participants found")
    return {"message": f"{len(winners)} winner(s) selected", "winner_ids": [w.id for w in winners]}


# --- Communications ---

@router.post("/{campaign_id}/communications", response_model=CampaignCommunicationResponse)
async def add_communication(
    campaign_id: int, comm: CampaignCommunicationCreate, db: Session = Depends(get_db)
):
    result = campaign_service.add_communication(db, campaign_id, comm)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


@router.get("/{campaign_id}/communications", response_model=List[CampaignCommunicationResponse])
async def list_communications(campaign_id: int, db: Session = Depends(get_db)):
    return campaign_service.get_campaign_communications(db, campaign_id)
