from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'organizations'

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    plan_type: Mapped[str] = mapped_column(String(50), nullable=False, default='free')

    teams: Mapped[list['Team']] = relationship(back_populates='organization', cascade='all, delete-orphan')
    athletes: Mapped[list['Athlete']] = relationship(back_populates='organization')
    videos: Mapped[list['Video']] = relationship(back_populates='organization')


class Team(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'teams'

    organization_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sport_type: Mapped[str] = mapped_column(String(100), nullable=False)
    season_label: Mapped[str | None] = mapped_column(String(100), nullable=True)

    organization: Mapped['Organization'] = relationship(back_populates='teams')
    members: Mapped[list['TeamMember']] = relationship(back_populates='team', cascade='all, delete-orphan')
    athletes: Mapped[list['Athlete']] = relationship(back_populates='team')
