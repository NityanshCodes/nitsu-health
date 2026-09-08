"""Health metrics API endpoints (longitudinal health data)."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.health import HealthMetricCreate, HealthMetricResponse, HealthMetricUpdate
from app.services import health_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/metrics", response_model=dict)
def list_metrics(
    metric_type: Optional[str] = Query(default=None),
    start: Optional[datetime] = Query(default=None),
    end: Optional[datetime] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = health_service.list_metrics(db, current_user, metric_type, start, end, limit, offset)
    return {
        "items": [HealthMetricResponse.model_validate(m) for m in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/metrics/types", response_model=list[str])
def list_metric_types(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[str]:
    return health_service.metric_types(db, current_user)


@router.post("/metrics", response_model=HealthMetricResponse, status_code=status.HTTP_201_CREATED)
def create_metric(
    data: HealthMetricCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthMetricResponse:
    metric = health_service.create_metric(db, current_user, data)
    log_action(db, "health_metric.create", user_id=current_user.id, entity_type="health_metric", entity_id=metric.id)
    return HealthMetricResponse.model_validate(metric)


@router.get("/metrics/{metric_id}", response_model=HealthMetricResponse)
def get_metric(
    metric_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthMetricResponse:
    metric = health_service.get_metric(db, current_user, metric_id)
    if metric is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
    return HealthMetricResponse.model_validate(metric)


@router.put("/metrics/{metric_id}", response_model=HealthMetricResponse)
def update_metric(
    metric_id: int,
    data: HealthMetricUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HealthMetricResponse:
    metric = health_service.update_metric(db, current_user, metric_id, data)
    if metric is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
    return HealthMetricResponse.model_validate(metric)


@router.delete("/metrics/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric(
    metric_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    deleted = health_service.delete_metric(db, current_user, metric_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
    log_action(db, "health_metric.delete", user_id=current_user.id, entity_type="health_metric", entity_id=metric_id)