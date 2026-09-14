"""Search API endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services import search_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(default=50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    results = search_service.search(db, current_user, q, limit)
    return {"query": q, "results": results, "total": len(results)}
