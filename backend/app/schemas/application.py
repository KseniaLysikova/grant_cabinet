from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field

from app.models import ApplicationStatus
from app.schemas.common import ORMBase
from app.schemas.auth import UserResponse


class ApplicationCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    project_goal: Optional[str] = None
    requested_amount: Optional[int] = Field(default=None, ge=0)
    competition_id: int


class ApplicationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = Field(default=None, min_length=10)
    project_goal: Optional[str] = None
    requested_amount: Optional[int] = Field(default=None, ge=0)
    status: Optional[ApplicationStatus] = None


class ApplicationFileResponse(ORMBase):
    id: int
    original_name: str
    stored_name: str
    mime_type: str
    size_bytes: int
    uploaded_at: datetime


class AIReviewResponse(ORMBase):
    id: int
    score: float
    summary: Optional[str]
    recommendations: Optional[str]
    created_at: datetime


class CompetitionShortResponse(ORMBase):
    id: int
    title: str
    deadline: date


class ApplicationResponse(ORMBase):
    id: int
    title: str
    description: str
    project_goal: Optional[str]
    requested_amount: Optional[int]
    status: ApplicationStatus
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    competition: CompetitionShortResponse
    owner: UserResponse
    files: list[ApplicationFileResponse] = []
    ai_review: Optional[AIReviewResponse] = None


class ApplicationListItem(ORMBase):
    id: int
    title: str
    status: ApplicationStatus
    requested_amount: Optional[int]
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    competition: CompetitionShortResponse


class AdminStatusUpdate(BaseModel):
    status: ApplicationStatus