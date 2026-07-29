from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from pathlib import Path
import pandas as pd
import tempfile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core.database import get_db
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStatusUpdate,
    CampaignQuestionCreate, CampaignQuestionResponse,
    CampaignParticipantResponse, CampaignWinnerCreate, CampaignWinnerResponse,
    CampaignCommunicationCreate, CampaignCommunicationResponse, CampaignStats,
    CampaignSubmission, CampaignParticipantBase, CampaignListResponse,
    CampaignParticipantListResponse
)
from app.services.campaign import CampaignService
from app.core.logging import logger

router = APIRouter()
campaign_service = CampaignService()

@router.get("/all", response_model=CampaignListResponse)
async def get_all_campaigns(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    campaigns, total = campaign_service.get_campaigns(db, page, size, search, status)
    return {
        "items": campaigns,
        "total": total,
        "page": page,
        "size": size
    }

@router.get("/stats", response_model=CampaignStats)
async def get_campaign_stats(db: Session = Depends(get_db)):
    return campaign_service.get_campaign_stats(db)

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = campaign_service.get_campaign_by_id(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/create", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    return campaign_service.create_campaign(db, campaign)

@router.post("/bulk-create", response_model=List[CampaignResponse])
async def create_bulk_campaigns(campaigns: List[CampaignCreate], db: Session = Depends(get_db)):
    return campaign_service.create_bulk_campaigns(db, campaigns)

@router.put("/update/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: int, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    updated_campaign = campaign_service.update_campaign(db, campaign_id, campaign)
    if not updated_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated_campaign

@router.put("/{campaign_id}/status", response_model=CampaignResponse)
async def update_campaign_status(campaign_id: int, status_update: CampaignStatusUpdate, db: Session = Depends(get_db)):
    updated_campaign = campaign_service.update_campaign_status(db, campaign_id, status_update.status)
    if not updated_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated_campaign

@router.post("/{campaign_id}/upload-banner", response_model=CampaignResponse)
async def upload_banner(
    campaign_id: int,
    banner_type: str = Query(..., regex="^(desktop|mobile)$"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    upload_dir = Path(f"images/campaigns/{campaign_id}")
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = Path(file.filename).suffix
    new_filename = f"{banner_type}_banner{file_ext}"
    file_path = upload_dir / new_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = str(file_path).replace("\\", "/")
    updated_campaign = campaign_service.update_campaign_image(db, campaign_id, image_url, banner_type)
    if not updated_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated_campaign

@router.post("/{campaign_id}/upload-image", response_model=CampaignResponse)
async def upload_promotional_image(
    campaign_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    upload_dir = Path(f"images/campaigns/{campaign_id}/promotional")
    os.makedirs(upload_dir, exist_ok=True)

    # Secure filename to prevent path traversal
    safe_filename = os.path.basename(file.filename)
    file_path = upload_dir / safe_filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = str(file_path).replace("\\", "/")
    updated_campaign = campaign_service.update_campaign_image(db, campaign_id, image_url, "promotional")
    if not updated_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated_campaign

# Questions
@router.get("/{campaign_id}/questions", response_model=List[CampaignQuestionResponse])
async def get_campaign_questions(campaign_id: int, db: Session = Depends(get_db)):
    return campaign_service.get_questions(db, campaign_id)

@router.post("/{campaign_id}/questions", response_model=List[CampaignQuestionResponse])
async def save_campaign_questions(campaign_id: int, questions: List[CampaignQuestionCreate], db: Session = Depends(get_db)):
    return campaign_service.save_questions(db, campaign_id, questions)

# Participants
@router.post("/{campaign_id}/participants", response_model=CampaignParticipantResponse)
async def add_participant(campaign_id: int, participant: CampaignParticipantBase, db: Session = Depends(get_db)):
    return campaign_service.add_participant(db, campaign_id, participant.model_dump())

@router.get("/{campaign_id}/participants", response_model=CampaignParticipantListResponse)
async def get_campaign_participants(
    campaign_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    participants, total = campaign_service.get_participants(db, campaign_id, page, size, search)
    return {
        "items": participants,
        "total": total,
        "page": page,
        "size": size
    }

@router.delete("/{campaign_id}/participants/{participant_id}")
async def remove_participant(campaign_id: int, participant_id: int, db: Session = Depends(get_db)):
    success = campaign_service.remove_participant(db, campaign_id, participant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    return {"message": "Participant removed successfully"}

@router.post("/{campaign_id}/submit")
async def submit_campaign_entry(campaign_id: int, submission: CampaignSubmission, db: Session = Depends(get_db)):
    success = campaign_service.submit_entry(db, campaign_id, submission.participant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Participant not found")
    return {"message": "Entry submitted successfully"}

@router.get("/{campaign_id}/participants/export")
async def export_participants(campaign_id: int, db: Session = Depends(get_db)):
    participants, _ = campaign_service.get_participants(db, campaign_id, page=1, size=1000000)

    data = []
    for p in participants:
        data.append({
            "Participant Name": p.participant_name,
            "Email": p.email,
            "Phone": p.phone,
            "Joined On": p.joined_on,
            "Submission Status": p.submission_status,
            "Is Verified": p.is_verified
        })

    df = pd.DataFrame(data)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name

    return FileResponse(tmp_path, filename=f"participants_campaign_{campaign_id}.xlsx", background=BackgroundTask(os.unlink, tmp_path))

# Winners
@router.get("/{campaign_id}/winners", response_model=List[CampaignWinnerResponse])
async def get_campaign_winners(
    campaign_id: int,
    winner_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return campaign_service.get_winners(db, campaign_id, winner_type)

@router.post("/{campaign_id}/winners", response_model=CampaignWinnerResponse)
async def assign_winner(campaign_id: int, winner: CampaignWinnerCreate, db: Session = Depends(get_db)):
    return campaign_service.assign_winner(db, campaign_id, winner)

@router.delete("/{campaign_id}/winners/{winner_id}")
async def remove_winner(campaign_id: int, winner_id: int, db: Session = Depends(get_db)):
    success = campaign_service.remove_winner(db, campaign_id, winner_id)
    if not success:
        raise HTTPException(status_code=404, detail="Winner not found")
    return {"message": "Winner removed successfully"}

# Communications
@router.post("/{campaign_id}/communicate", response_model=CampaignCommunicationResponse)
async def trigger_communication(campaign_id: int, communication: CampaignCommunicationCreate, db: Session = Depends(get_db)):
    return campaign_service.trigger_communication(db, campaign_id, communication)

@router.get("/{campaign_id}/communications", response_model=List[CampaignCommunicationResponse])
async def get_campaign_communications(campaign_id: int, db: Session = Depends(get_db)):
    return campaign_service.get_communications(db, campaign_id)
