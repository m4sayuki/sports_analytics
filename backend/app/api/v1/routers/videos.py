from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoRead, VideoUpdate

router = APIRouter(prefix='/videos', tags=['videos'])


@router.get('', response_model=list[VideoRead])
def list_videos(
    organization_id: UUID | None = None,
    team_id: UUID | None = None,
    athlete_id: UUID | None = None,
    status_value: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Video]:
    stmt = select(Video)
    if organization_id:
        stmt = stmt.where(Video.organization_id == organization_id)
    if team_id:
        stmt = stmt.where(Video.team_id == team_id)
    if athlete_id:
        stmt = stmt.where(Video.athlete_id == athlete_id)
    if status_value:
        stmt = stmt.where(Video.status == status_value)
    stmt = stmt.order_by(Video.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


@router.post('', response_model=VideoRead, status_code=status.HTTP_201_CREATED)
def create_video(payload: VideoCreate, db: Session = Depends(get_db)) -> Video:
    video = Video(**payload.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.get('/{video_id}', response_model=VideoRead)
def get_video(video_id: UUID, db: Session = Depends(get_db)) -> Video:
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Video not found')
    return video


@router.patch('/{video_id}', response_model=VideoRead)
def update_video(video_id: UUID, payload: VideoUpdate, db: Session = Depends(get_db)) -> Video:
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Video not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(video, field, value)
    db.commit()
    db.refresh(video)
    return video


@router.delete('/{video_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_video(video_id: UUID, db: Session = Depends(get_db)) -> None:
    video = db.get(Video, video_id)
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Video not found')
    db.delete(video)
    db.commit()
