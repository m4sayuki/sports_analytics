import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class UserRole(str, enum.Enum):
    admin = 'admin'
    coach = 'coach'
    analyst = 'analyst'
    athlete = 'athlete'


class TeamMemberRole(str, enum.Enum):
    owner = 'owner'
    coach = 'coach'
    manager = 'manager'
    viewer = 'viewer'


class VideoStatus(str, enum.Enum):
    uploaded = 'uploaded'
    processing = 'processing'
    ready = 'ready'
    failed = 'failed'


class AnalysisSessionStatus(str, enum.Enum):
    draft = 'draft'
    in_progress = 'in_progress'
    completed = 'completed'
    archived = 'archived'


class PointSourceType(str, enum.Enum):
    manual = 'manual'
    interpolated = 'interpolated'
    auto_detected = 'auto_detected'


class AnalysisJobStatus(str, enum.Enum):
    queued = 'queued'
    running = 'running'
    succeeded = 'succeeded'
    failed = 'failed'
