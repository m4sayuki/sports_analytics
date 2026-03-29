from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TeamMemberRole, TimestampMixin, UUIDPrimaryKeyMixin, UserRole


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    team_memberships: Mapped[list['TeamMember']] = relationship(back_populates='user', cascade='all, delete-orphan')
    uploaded_videos: Mapped[list['Video']] = relationship(back_populates='uploaded_by_user')
    analysis_sessions: Mapped[list['AnalysisSession']] = relationship(back_populates='created_by_user')
    created_track_points: Mapped[list['TrackPoint']] = relationship(back_populates='created_by_user')


class TeamMember(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'team_members'
    __table_args__ = (UniqueConstraint('team_id', 'user_id', name='uq_team_members_team_user'),)

    team_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    membership_role: Mapped[TeamMemberRole] = mapped_column(nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)

    team: Mapped['Team'] = relationship(back_populates='members')
    user: Mapped['User'] = relationship(back_populates='team_memberships')
