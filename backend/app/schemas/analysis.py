from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AnalysisSessionCreate(BaseModel):
    video_id: UUID
    athlete_id: UUID | None = None
    created_by_user_id: UUID
    session_name: str = Field(min_length=1, max_length=255)
    analysis_type: str = Field(min_length=1, max_length=100)
    status: str = 'draft'
    note: str | None = None


class AnalysisSessionUpdate(BaseModel):
    athlete_id: UUID | None = None
    session_name: str | None = None
    analysis_type: str | None = None
    status: str | None = None
    note: str | None = None


class AnalysisSessionRead(ORMModel):
    id: UUID
    video_id: UUID
    athlete_id: UUID | None
    created_by_user_id: UUID
    session_name: str
    analysis_type: str
    status: str
    note: str | None
    created_at: datetime
    updated_at: datetime


class MotionTrackCreate(BaseModel):
    analysis_session_id: UUID
    name: str = Field(min_length=1, max_length=255)
    body_part: str | None = None
    color_hex: str = Field(min_length=4, max_length=7)
    sort_order: int = 0
    is_visible: bool = True


class MotionTrackUpdate(BaseModel):
    name: str | None = None
    body_part: str | None = None
    color_hex: str | None = None
    sort_order: int | None = None
    is_visible: bool | None = None


class MotionTrackRead(ORMModel):
    id: UUID
    analysis_session_id: UUID
    name: str
    body_part: str | None
    color_hex: str
    sort_order: int
    is_visible: bool
    created_at: datetime
    updated_at: datetime


class TrackPointCreate(BaseModel):
    motion_track_id: UUID
    frame_index: int | None = None
    time_ms: int = Field(ge=0)
    x_norm: Decimal = Field(ge=0, le=1)
    y_norm: Decimal = Field(ge=0, le=1)
    confidence: Decimal | None = None
    source_type: str = 'manual'
    created_by_user_id: UUID | None = None


class TrackPointBulkCreate(BaseModel):
    points: list[TrackPointCreate]


class TrackPointUpdate(BaseModel):
    frame_index: int | None = None
    time_ms: int | None = Field(default=None, ge=0)
    x_norm: Decimal | None = Field(default=None, ge=0, le=1)
    y_norm: Decimal | None = Field(default=None, ge=0, le=1)
    confidence: Decimal | None = None
    source_type: str | None = None


class TrackPointRead(ORMModel):
    id: UUID
    motion_track_id: UUID
    frame_index: int | None
    time_ms: int
    x_norm: Decimal
    y_norm: Decimal
    confidence: Decimal | None
    source_type: str
    created_by_user_id: UUID | None
    created_at: datetime
