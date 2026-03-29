from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.athlete import Athlete
from app.schemas.athlete import AthleteCreate, AthleteRead, AthleteUpdate

router = APIRouter(prefix='/athletes', tags=['athletes'])


@router.get('', response_model=list[AthleteRead])
def list_athletes(
    organization_id: UUID | None = None,
    team_id: UUID | None = None,
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Athlete]:
    stmt = select(Athlete)
    if organization_id:
        stmt = stmt.where(Athlete.organization_id == organization_id)
    if team_id:
        stmt = stmt.where(Athlete.team_id == team_id)
    if q:
        stmt = stmt.where(Athlete.name.ilike(f'%{q}%'))
    stmt = stmt.order_by(Athlete.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


@router.post('', response_model=AthleteRead, status_code=status.HTTP_201_CREATED)
def create_athlete(payload: AthleteCreate, db: Session = Depends(get_db)) -> Athlete:
    athlete = Athlete(**payload.model_dump())
    db.add(athlete)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.get('/{athlete_id}', response_model=AthleteRead)
def get_athlete(athlete_id: UUID, db: Session = Depends(get_db)) -> Athlete:
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Athlete not found')
    return athlete


@router.patch('/{athlete_id}', response_model=AthleteRead)
def update_athlete(athlete_id: UUID, payload: AthleteUpdate, db: Session = Depends(get_db)) -> Athlete:
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Athlete not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(athlete, field, value)
    db.commit()
    db.refresh(athlete)
    return athlete


@router.delete('/{athlete_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_athlete(athlete_id: UUID, db: Session = Depends(get_db)) -> None:
    athlete = db.get(Athlete, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Athlete not found')
    db.delete(athlete)
    db.commit()
