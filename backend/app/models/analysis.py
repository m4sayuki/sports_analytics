from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import (
    AnalysisJobStatus,
    AnalysisSessionStatus,
    Base,
    PointSourceType,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class AnalysisSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'analysis_sessions'

    video_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    athlete_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey('athletes.id', ondelete='SET NULL'), nullable=True, index=True)
    created_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    session_name: Mapped[str] = mapped_column(String(255), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[AnalysisSessionStatus] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    video: Mapped['Video'] = relationship(back_populates='analysis_sessions')
    athlete: Mapped['Athlete | None'] = relationship(back_populates='analysis_sessions')
    created_by_user: Mapped['User'] = relationship(back_populates='analysis_sessions')
    motion_tracks: Mapped[list['MotionTrack']] = relationship(back_populates='analysis_session', cascade='all, delete-orphan')
    outputs: Mapped[list['AnalysisOutput']] = relationship(back_populates='analysis_session', cascade='all, delete-orphan')
    keypoint_series: Mapped[list['KeypointSeries']] = relationship(back_populates='analysis_session', cascade='all, delete-orphan')


class MotionTrack(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'motion_tracks'

    analysis_session_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('analysis_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    body_part: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color_hex: Mapped[str] = mapped_column(String(7), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_visible: Mapped[bool] = mapped_column(nullable=False, default=True)

    analysis_session: Mapped['AnalysisSession'] = relationship(back_populates='motion_tracks')
    points: Mapped[list['TrackPoint']] = relationship(back_populates='motion_track', cascade='all, delete-orphan')


class TrackPoint(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'track_points'
    __table_args__ = (
        CheckConstraint('x_norm >= 0 AND x_norm <= 1', name='ck_track_points_x_norm_range'),
        CheckConstraint('y_norm >= 0 AND y_norm <= 1', name='ck_track_points_y_norm_range'),
        Index('ix_track_points_track_time', 'motion_track_id', 'time_ms'),
    )

    motion_track_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('motion_tracks.id', ondelete='CASCADE'), nullable=False, index=True)
    frame_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    x_norm: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    y_norm: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    source_type: Mapped[PointSourceType] = mapped_column(nullable=False)
    created_by_user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    motion_track: Mapped['MotionTrack'] = relationship(back_populates='points')
    created_by_user: Mapped['User | None'] = relationship(back_populates='created_track_points')


class AnalysisJob(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'analysis_jobs'

    video_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('videos.id', ondelete='CASCADE'), nullable=False, index=True)
    analysis_session_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey('analysis_sessions.id', ondelete='SET NULL'), nullable=True, index=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[AnalysisJobStatus] = mapped_column(nullable=False)
    requested_by_user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    worker_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    video: Mapped['Video'] = relationship(back_populates='analysis_jobs')


class AnalysisOutput(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'analysis_outputs'

    analysis_session_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('analysis_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    output_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    analysis_session: Mapped['AnalysisSession'] = relationship(back_populates='outputs')


class KeypointSeries(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'keypoint_series'
    __table_args__ = (
        CheckConstraint('x_norm >= 0 AND x_norm <= 1', name='ck_keypoint_series_x_norm_range'),
        CheckConstraint('y_norm >= 0 AND y_norm <= 1', name='ck_keypoint_series_y_norm_range'),
        Index('ix_keypoint_series_session_time', 'analysis_session_id', 'time_ms'),
    )

    analysis_session_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('analysis_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    keypoint_name: Mapped[str] = mapped_column(String(100), nullable=False)
    frame_index: Mapped[int] = mapped_column(Integer, nullable=False)
    time_ms: Mapped[int] = mapped_column(BigInteger, nullable=False)
    x_norm: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    y_norm: Mapped[Decimal] = mapped_column(Numeric(8, 6), nullable=False)
    z_norm: Mapped[Decimal | None] = mapped_column(Numeric(8, 6), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    analysis_session: Mapped['AnalysisSession'] = relationship(back_populates='keypoint_series')
