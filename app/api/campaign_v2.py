from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
from pathlib import Path
import os

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.campaign import (
    CampaignV2Response, CampaignParticipationCreate, CampaignParticipationResponse,
    CampaignResultsResponse, CreateCampaignRequestV2, UpdateCampaignRequestV2,
    PatchCampaignRequestV2, CampaignListResponseV2, CampaignResultsV2,
    CampaignStatsV2, BulkActionRequestV2, BulkActionResponseV2
)
from app.services.campaign import CampaignService
from app.services.storage import StorageService
from app.api.auth import get_current_user_admin
import pandas as pd
import tempfile
import os
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

router = APIRouter()
campaign_service = CampaignService()
storage_service = StorageService()

@router.get("", response_model=CampaignListResponseV2)
async def list_campaigns(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    campaigns, total = campaign_service.get_campaigns_v2_admin(db, page, per_page, status, search)
    return {
        "items": campaigns,
        "total": total,
        "page": page,
        "per_page": per_page
    }

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

@router.get("/{id}/results", response_model=CampaignResultsV2)
async def get_campaign_results(id: str, db: Session = Depends(get_db)):
    results = campaign_service.get_campaign_results_v2(db, id)
    if not results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return results

@router.get("/stats", response_model=CampaignStatsV2)
async def get_campaign_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_admin)):
    return campaign_service.get_campaign_stats_v2(db)

@router.post("", response_model=CampaignV2Response)
async def create_campaign(
    campaign: CreateCampaignRequestV2,
    current_user: User = Depends(get_current_user_admin),
    db: Session = Depends(get_db)
):
    return campaign_service.create_campaign_v2(db, campaign.model_dump(by_alias=True), str(current_user.id))

@router.put("/{id}", response_model=CampaignV2Response)
async def update_campaign(
    id: str,
    campaign: UpdateCampaignRequestV2,
    current_user: User = Depends(get_current_user_admin),
    db: Session = Depends(get_db)
):
    updated = campaign_service.update_campaign_v2(db, id, campaign.model_dump(exclude_unset=True, by_alias=True), str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated

@router.post("/{id}/reset-participants")
async def reset_campaign_participants(
    id: str,
    current_user: User = Depends(get_current_user_admin),
    db: Session = Depends(get_db)
):
    if not campaign_service.reset_participants_v2(db, id):
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "All participants have been removed from the campaign"}

@router.patch("/{id}", response_model=CampaignV2Response)
async def patch_campaign(
    id: str,
    updates: PatchCampaignRequestV2,
    current_user: User = Depends(get_current_user_admin),
    db: Session = Depends(get_db)
):
    updated = campaign_service.patch_campaign_v2(db, id, updates.model_dump(exclude_unset=True, by_alias=True), str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated

@router.delete("/{id}")
async def delete_campaign(
    id: str,
    current_user: User = Depends(get_current_user_admin),
    db: Session = Depends(get_db)
):
    if not campaign_service.delete_campaign_v2(db, id):
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Campaign deleted"}

@router.post("/{id}/publish", response_model=CampaignV2Response)
async def publish_campaign(
    id: str,
    force_data: dict = {},
    current_user: User = Depends(get_current_user_admin),
    db: Session = Depends(get_db)
):
    from app.models.campaign import CampaignStatusV2
    updated = campaign_service.patch_campaign_v2(db, id, {"status": CampaignStatusV2.ACTIVE}, str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated

@router.post("/{id}/unpublish", response_model=CampaignV2Response)
async def unpublish_campaign(
    id: str,
    current_user: User = Depends(get_current_user_admin),
    db: Session = Depends(get_db)
):
    from app.models.campaign import CampaignStatusV2
    updated = campaign_service.patch_campaign_v2(db, id, {"status": CampaignStatusV2.paused}, str(current_user.id))
    if not updated:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return updated

@router.get("/{id}/export")
async def export_campaign_data(id: str, format: str = "csv", db: Session = Depends(get_db), current_user: User = Depends(get_current_user_admin)):
    from app.models.campaign import CampaignParticipation, CampaignV2
    from app.models.user import User
    from app.models.customer import Customer

    query = db.query(
        CampaignParticipation,
        CampaignV2.title.label("campaign_name"),
        User.email.label("user_email"),
        User.mobile.label("user_mobile"),
        Customer.first_name,
        Customer.last_name
    ).join(
        CampaignV2, CampaignParticipation.campaign_id == CampaignV2.id
    ).outerjoin(
        User, CampaignParticipation.user_id == User.id
    ).outerjoin(
        Customer, User.customer_id == Customer.id
    ).filter(CampaignParticipation.campaign_id == id)

    results = query.all()

    data = []
    for p, campaign_name, user_email, user_mobile, first_name, last_name in results:
        user_name = "N/A"
        if first_name or last_name:
            user_name = f"{first_name or ''} {last_name or ''}".strip()

        row = {
            "participation_id": p.id,
            "campaign_name": campaign_name,
            "user_id": p.user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_mobile": user_mobile,
            "participation_date": p.participation_date,
            "status": p.status
        }
        if p.responses:
            row.update(p.responses)
        data.append(row)

    df = pd.DataFrame(data)

    suffix = ".csv" if format == "csv" else ".xlsx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        if format == "csv":
            df.to_csv(tmp.name, index=False)
        else:
            df.to_excel(tmp.name, index=False)
        tmp_path = tmp.name

    return FileResponse(tmp_path, filename=f"campaign_{id}_export{suffix}", background=BackgroundTask(os.unlink, tmp_path))

@router.post("/bulk/publish", response_model=BulkActionResponseV2)
async def bulk_publish(request: BulkActionRequestV2, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_admin)):
    return campaign_service.bulk_action_v2(db, request.ids, 'publish', request.force, str(current_user.id))

@router.post("/bulk/unpublish", response_model=BulkActionResponseV2)
async def bulk_unpublish(request: BulkActionRequestV2, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_admin)):
    return campaign_service.bulk_action_v2(db, request.ids, 'unpublish', request.force, str(current_user.id))

@router.post("/bulk/delete", response_model=BulkActionResponseV2)
async def bulk_delete(request: BulkActionRequestV2, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_admin)):
    return campaign_service.bulk_action_v2(db, request.ids, 'delete', request.force, str(current_user.id))

@router.post("/bulk/pause", response_model=BulkActionResponseV2)
async def bulk_pause(request: BulkActionRequestV2, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_admin)):
    return campaign_service.bulk_action_v2(db, request.ids, 'pause', request.force, str(current_user.id))

@router.post("/bulk/action", response_model=BulkActionResponseV2)
async def bulk_action(request: BulkActionRequestV2, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_admin)):
    return campaign_service.bulk_action_v2(db, request.ids, request.action, request.force, str(current_user.id))

@router.post("/{id}/upload-image", response_model=CampaignV2Response)
async def upload_campaign_image(
    id: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_admin)
):
    # Get existing campaign to check for old image
    campaign = campaign_service.get_campaign_v2_by_id(db, id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Delete old image from R2 if it exists
    if campaign.image_url and campaign.image_url.startswith("http"):
        await storage_service.delete_image(campaign.image_url)

    # Upload new image to R2
    image_url = await storage_service.upload_image(image, folder="campaigns")

    # Update the campaign's image_url in the database
    updated_campaign = campaign_service.update_campaign_v2_image(db, id, image_url)

    return updated_campaign
