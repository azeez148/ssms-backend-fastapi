from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagMapRequest
from app.services.tag import TagService

router = APIRouter()
tag_service = TagService()

@router.get("/all", response_model=List[TagResponse])
async def get_all_tags(db: Session = Depends(get_db)):
    return tag_service.get_all_tags(db)

@router.post("/add", response_model=TagResponse)
async def add_tag(tag: TagCreate, db: Session = Depends(get_db)):
    return tag_service.create_tag(db, tag)

@router.put("/update/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, tag: TagCreate, db: Session = Depends(get_db)):
    # Note: TagCreate is used for the body as per common pattern,
    # but we wrap it in TagUpdate to pass to service.
    tag_update = TagUpdate(id=tag_id, **tag.model_dump())
    updated_tag = tag_service.update_tag(db, tag_update)
    if not updated_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return updated_tag

@router.delete("/delete/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    success = tag_service.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"message": "Tag deleted successfully"}

@router.post("/map")
async def map_tags_to_products(map_data: TagMapRequest, db: Session = Depends(get_db)):
    return tag_service.map_tags_to_products(db, map_data)
