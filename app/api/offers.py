from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.offer import UpdateProductOfferRequest
from app.services.offer import OfferService

router = APIRouter()
offer_service = OfferService()

@router.post("/updateOffer")
async def update_product_offer(
    request: UpdateProductOfferRequest,
    db: Session = Depends(get_db)
):
    try:
        return offer_service.update_product_offer(db, request.product_ids, request.offer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
