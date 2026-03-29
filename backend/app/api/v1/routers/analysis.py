from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.analysis import AnalysisSession, MotionTrack, TrackPoint
from app.schemas.analysis import (
    AnalysisSessionCreate,
    AnalysisSessionRead,
    AnalysisSessionUpdate,
    MotionTrackCreate,
    MotionTrackRead,
    MotionTrackUpdate,
    TrackPointBulkCreate,
    TrackPointCreate,
    TrackPointRead,
    TrackPointUpdate,
)

router = APIRouter(tags=['analysis'])


@router.get('/analysis-sessions', response_model=list[AnalysisSessionRead])
def list_analysis_sessions(
    video_id: UUID | None = None,
    athlete_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[AnalysisSession]:
    stmt = select(AnalysisSession)
    if video_id:
        stmt = stmt.where(AnalysisSession.video_id == video_id)
    if athlete_id:
        stmt = stmt.where(AnalysisSession.athlete_id == athlete_id)
    stmt = stmt.order_by(AnalysisSession.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


@router.post('/analysis-sessions', response_model=AnalysisSessionRead, status_code=status.HTTP_201_CREATED)
def create_analysis_session(payload: AnalysisSessionCreate, db: Session = Depends(get_db)) -> AnalysisSession:
    session_obj = AnalysisSession(**payload.model_dump())
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)
    return session_obj


@router.get('/analysis-sessions/{session_id}', response_model=AnalysisSessionRead)
def get_analysis_session(session_id: UUID, db: Session = Depends(get_db)) -> AnalysisSession:
    session_obj = db.get(AnalysisSession, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Analysis session not found')
    return session_obj


@router.patch('/analysis-sessions/{session_id}', response_model=AnalysisSessionRead)
def update_analysis_session(session_id: UUID, payload: AnalysisSessionUpdate, db: Session = Depends(get_db)) -> AnalysisSession:
    session_obj = db.get(AnalysisSession, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Analysis session not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(session_obj, field, value)
    db.commit()
    db.refresh(session_obj)
    return session_obj


@router.delete('/analysis-sessions/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis_session(session_id: UUID, db: Session = Depends(get_db)) -> None:
    session_obj = db.get(AnalysisSession, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Analysis session not found')
    db.delete(session_obj)
    db.commit()


@router.get('/analysis-sessions/{session_id}/tracks', response_model=list[MotionTrackRead])
def list_tracks(session_id: UUID, db: Session = Depends(get_db)) -> list[MotionTrack]:
    stmt = select(MotionTrack).where(MotionTrack.analysis_session_id == session_id).order_by(MotionTrack.sort_order.asc(), MotionTrack.created_at.asc())
    return list(db.scalars(stmt).all())


@router.post('/analysis-sessions/{session_id}/tracks', response_model=MotionTrackRead, status_code=status.HTTP_201_CREATED)
def create_track(session_id: UUID, payload: MotionTrackCreate, db: Session = Depends(get_db)) -> MotionTrack:
    data = payload.model_dump()
    data['analysis_session_id'] = session_id
    track = MotionTrack(**data)
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


@router.patch('/tracks/{track_id}', response_model=MotionTrackRead)
def update_track(track_id: UUID, payload: MotionTrackUpdate, db: Session = Depends(get_db)) -> MotionTrack:
    track = db.get(MotionTrack, track_id)
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Track not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(track, field, value)
    db.commit()
    db.refresh(track)
    return track


@router.delete('/tracks/{track_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_track(track_id: UUID, db: Session = Depends(get_db)) -> None:
    track = db.get(MotionTrack, track_id)
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Track not found')
    db.delete(track)
    db.commit()


@router.get('/tracks/{track_id}/points', response_model=list[TrackPointRead])
def list_track_points(
    track_id: UUID,
    from_ms: int | None = Query(default=None, ge=0),
    to_ms: int | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
) -> list[TrackPoint]:
    stmt = select(TrackPoint).where(TrackPoint.motion_track_id == track_id)
    if from_ms is not None:
        stmt = stmt.where(TrackPoint.time_ms >= from_ms)
    if to_ms is not None:
        stmt = stmt.where(TrackPoint.time_ms <= to_ms)
    stmt = stmt.order_by(TrackPoint.time_ms.asc())
    return list(db.scalars(stmt).all())


@router.post('/tracks/{track_id}/points', response_model=TrackPointRead, status_code=status.HTTP_201_CREATED)
def create_track_point(track_id: UUID, payload: TrackPointCreate, db: Session = Depends(get_db)) -> TrackPoint:
    data = payload.model_dump()
    data['motion_track_id'] = track_id
    point = TrackPoint(**data)
    db.add(point)
    db.commit()
    db.refresh(point)
    return point


@router.post('/tracks/{track_id}/points/bulk', response_model=list[TrackPointRead], status_code=status.HTTP_201_CREATED)
def bulk_create_track_points(track_id: UUID, payload: TrackPointBulkCreate, db: Session = Depends(get_db)) -> list[TrackPoint]:
    points: list[TrackPoint] = []
    for item in payload.points:
        data = item.model_dump()
        data['motion_track_id'] = track_id
        points.append(TrackPoint(**data))
    db.add_all(points)
    db.commit()
    for point in points:
        db.refresh(point)
    return points


@router.patch('/track-points/{point_id}', response_model=TrackPointRead)
def update_track_point(point_id: UUID, payload: TrackPointUpdate, db: Session = Depends(get_db)) -> TrackPoint:
    point = db.get(TrackPoint, point_id)
    if not point:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Track point not found')
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(point, field, value)
    db.commit()
    db.refresh(point)
    return point


@router.delete('/track-points/{point_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_track_point(point_id: UUID, db: Session = Depends(get_db)) -> None:
    point = db.get(TrackPoint, point_id)
    if not point:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Track point not found')
    db.delete(point)
    db.commit()


@router.delete('/tracks/{track_id}/points', status_code=status.HTTP_204_NO_CONTENT)
def clear_track_points(track_id: UUID, db: Session = Depends(get_db)) -> None:
    db.execute(delete(TrackPoint).where(TrackPoint.motion_track_id == track_id))
    db.commit()
