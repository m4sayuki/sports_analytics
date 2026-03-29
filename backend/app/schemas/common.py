from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampRead(ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class IDResponse(BaseModel):
    id: UUID


class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


DateType = date
DateTimeType = datetime
DecimalType = Decimal
