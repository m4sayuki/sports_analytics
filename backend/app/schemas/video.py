from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class VideoBase(BaseModel):
    organization_id: UUID
    team_id: UUID | None = None
    athlete_id: UUID | None = None
    uploaded_by_user_id: UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sport_type: str = Field(min_length=1, max_length=100)
    capture_date: date | None = None
    recorded_at: datetime | None = None
    camera_view: str | None = None
    frame_rate: Decimal | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    status: str


class VideoCreate(VideoBase):
    pass


class VideoUpdate(BaseModel):
    team_id: UUID | None = None
    athlete_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    sport_type: str | None = None
    capture_date: date | None = None
    recorded_at: datetime | None = None
    camera_view: str | None = None
    frame_rate: Decimal | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    status: str | None = None


class VideoRead(ORMModel):
    id: UUID
    organization_id: UUID
    team_id: UUID | None
    athlete_id: UUID | None
    uploaded_by_user_id: UUID
    title: str
    description: str | None
    sport_type: str
    capture_date: date | None
    recorded_at: datetime | None
    camera_view: str | None
    frame_rate: Decimal | None
    duration_ms: int | None
    status: str
