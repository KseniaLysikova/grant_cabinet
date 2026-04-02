from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models import CompetitionStatus
from app.schemas.common import ORMBase


class CompetitionCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    deadline: date
    status: CompetitionStatus = CompetitionStatus.open


class CompetitionResponse(ORMBase):
    id: int
    title: str
    description: str
    deadline: date
    status: CompetitionStatus
    created_at: datetime