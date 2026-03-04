from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from enum import Enum

class KafkaEventType(str, Enum):
    SALE_CREATED = "sale_created"
    PURCHASE_CREATED = "purchase_created"
    DAY_SUMMARY_GENERATED = "day_summary_generated"
    REPORT_GENERATED = "report_generated"

class KafkaEvent(BaseModel):
    event_type: KafkaEventType
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True
