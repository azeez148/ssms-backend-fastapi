from pydantic import BaseModel

class StatusResponse(BaseModel):
    dayStarted: bool
    opening_balance: float
