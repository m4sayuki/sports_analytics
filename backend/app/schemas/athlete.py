from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class AthleteBase(BaseModel):
    organization_id: UUID
    team_id: UUID | None = None
    external_code: str | None = None
    name: str = Field(min_length=1, max_length=255)
    kana_name: str | None = None
    birth_date: date | None = None
    sex: str | None = None
    dominant_side: str | None = None
    position_name: str | None = None
    height_cm: Decimal | None = None
    weight_kg: Decimal | None = None
    note: str | None = None


class AthleteCreate(AthleteBase):
    pass


class AthleteUpdate(BaseModel):
    team_id: UUID | None = None
    external_code: str | None = None
    name: str | None = None
    kana_name: str | None = None
    birth_date: date | None = None
    sex: str | None = None
    dominant_side: str | None = None
    position_name: str | None = None
    height_cm: Decimal | None = None
    weight_kg: Decimal | None = None
    note: str | None = None


class AthleteRead(ORMModel):
    id: UUID
    organization_id: UUID
    team_id: UUID | None
    external_code: str | None
    name: str
    kana_name: str | None
    birth_date: date | None
    sex: str | None
    dominant_side: str | None
    position_name: str | None
    height_cm: Decimal | None
    weight_kg: Decimal | None
    note: str | None
