from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Athlete(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = 'athletes'

    organization_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    team_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='SET NULL'), nullable=True, index=True)
    external_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kana_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sex: Mapped[str | None] = mapped_column(String(30), nullable=True)
    dominant_side: Mapped[str | None] = mapped_column(String(20), nullable=True)
    position_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    organization: Mapped['Organization'] = relationship(back_populates='athletes')
    team: Mapped['Team | None'] = relationship(back_populates='athletes')
    videos: Mapped[list['Video']] = relationship(back_populates='athlete')
    analysis_sessions: Mapped[list['AnalysisSession']] = relationship(back_populates='athlete')
