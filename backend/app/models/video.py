from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, VideoStatus


class Video(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'videos'
    __table_args__ = (Index('ix_videos_org_team_athlete', 'organization_id', 'team_id', 'athlete_id'),)

    organization_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    team_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    athlete_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey('athletes.id', ondelete='SET NULL'), nullable=True, index=True)
    uploaded_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sport_type: Mapped[str] = mapped_column(String(100), nullable=False)
    capture_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    recorded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    camera_view: Mapped[str | None] = mapped_column(String(50), nullable=True)
    frame_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 3), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[VideoStatus] = mapped_column(nullable=False)

    organization: Mapped['Organization'] = relationship(back_populates='videos')
    athlete: Mapped['Athlete | None'] = relationship(back_populates='videos')
    uploaded_by_user: Mapped['User'] = relationship(back_populates='uploaded_videos')
    files: Mapped[list['VideoFile']] = relationship(back_populates='video', cascade='all, delete-orphan')
    analysis_sessions: Mapped[list['AnalysisSession']] = relationship(back_populates='video', cascade='all, delete-orphan')
    analysis_jobs: Mapped[list['AnalysisJob']] = relationship(back_populates='video', cascade='all, delete-orphan')


class VideoFile(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'video_files'

    video_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False, default='s3')
    bucket_name: Mapped[str] = mapped_column(String(255), nullable=False)
    object_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width_px: Mapped[int | None] = mapped_column(nullable=True)
    height_px: Mapped[int | None] = mapped_column(nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    video: Mapped['Video'] = relationship(back_populates='files')
