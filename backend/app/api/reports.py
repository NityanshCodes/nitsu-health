"""Reports API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.report import HealthReport
from app.services import ai_report_service
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def list_reports(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = ai_report_service.list_reports(db, current_user, limit, offset)
    return {
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "report_type": r.report_type,
                "summary": r.summary,
                "status": r.status,
                "generated_at": str(r.generated_at) if r.generated_at else None,
                "created_at": str(r.created_at),
            }
            for r in items
        ],
        "total": total,
    }


@router.get("/latest")
def latest_report(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    report = (
        db.query(HealthReport)
        .filter(HealthReport.user_id == current_user.id)
        .order_by(HealthReport.created_at.desc())
        .first()
    )
    if not report:
        return {
            "user_id": current_user.id,
            "title": "No reports yet",
            "status": "none",
            "summary": "Generate your first wellness report to get started.",
        }
    return {
        "user_id": report.user_id,
        "title": report.title,
        "report_type": report.report_type,
        "status": report.status,
        "summary": report.summary,
        "report_data": report.report_data,
        "generated_at": str(report.generated_at) if report.generated_at else None,
    }


@router.post("/generate", status_code=status.HTTP_201_CREATED)
def generate_report(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    report = ai_report_service.generate_report(db, current_user)
    log_action(db, "report.generate", user_id=current_user.id, entity_type="health_report", entity_id=report.id)
    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "status": report.status,
        "summary": report.summary,
        "generated_at": str(report.generated_at),
    }


@router.get("/{report_id}")
def get_report(
    report_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    report = ai_report_service.get_report(db, current_user, report_id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "summary": report.summary,
        "report_data": report.report_data,
        "status": report.status,
        "generated_at": str(report.generated_at) if report.generated_at else None,
    }
