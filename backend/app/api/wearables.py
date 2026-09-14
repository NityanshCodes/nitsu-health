"""Wearables / Fitbit integration API endpoints."""

import secrets
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.wearable_connection import WearableConnection
from app.providers.wearables.fitbit import FitbitProvider
from app.providers.wearables.demo import DemoWearableProvider
from app.utils.audit import log_action
from app.utils.auth import get_current_user

router = APIRouter(prefix="/wearables", tags=["wearables"])

PROVIDER_NAME = "fitbit"


def _get_provider():
    fitbit = FitbitProvider()
    if fitbit.is_configured():
        return fitbit
    return DemoWearableProvider()


@router.get("/status")
def wearable_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Show connection status for all wearable providers."""
    connections = (
        db.query(WearableConnection)
        .filter(WearableConnection.user_id == current_user.id)
        .all()
    )
    provider = _get_provider()
    return {
        "configured": provider.is_configured(),
        "config_note": (
            None if provider.is_configured()
            else "Fitbit credentials not configured. Set FITBIT_CLIENT_ID and FITBIT_CLIENT_SECRET."
        ),
        "connections": [
            {
                "provider": c.provider,
                "status": c.status,
                "last_synced_at": str(c.last_synced_at) if c.last_synced_at else None,
            }
            for c in connections
        ],
    }


@router.get("/fitbit/connect")
def fitbit_connect(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Start Fitbit OAuth flow — returns authorization URL."""
    provider = _get_provider()
    state = secrets.token_urlsafe(32)
    return {
        "auth_url": provider.auth_url(state),
        "state": state,
        "note": "Demo mode — mock data will be returned." if isinstance(provider, DemoWearableProvider) else None,
    }


@router.get("/fitbit/callback")
async def fitbit_callback(
    code: str = Query(...),
    state: str = Query(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Handle Fitbit OAuth callback — exchange code for tokens."""
    provider = _get_provider()
    try:
        token_data = await provider.exchange_code(code)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Token exchange failed: {exc}") from exc

    # Upsert connection
    conn = (
        db.query(WearableConnection)
        .filter(WearableConnection.user_id == current_user.id, WearableConnection.provider == PROVIDER_NAME)
        .first()
    )
    now = datetime.utcnow()
    if conn is None:
        conn = WearableConnection(user_id=current_user.id, provider=PROVIDER_NAME)
        db.add(conn)

    conn.status = "connected"
    conn.access_token_enc = token_data.get("access_token", "")
    conn.refresh_token_enc = token_data.get("refresh_token", "")
    conn.token_expires_at = now.replace(hour=now.hour + (token_data.get("expires_in", 28800) // 3600))
    conn.last_synced_at = now
    db.commit()

    log_action(db, "wearable.connect", user_id=current_user.id, entity_type="wearable_connection", details={"provider": PROVIDER_NAME})

    return {"status": "connected", "provider": PROVIDER_NAME}


@router.post("/fitbit/sync")
async def fitbit_sync(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Sync data from Fitbit (or demo provider)."""
    conn = (
        db.query(WearableConnection)
        .filter(WearableConnection.user_id == current_user.id, WearableConnection.provider == PROVIDER_NAME)
        .first()
    )
    if conn is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Fitbit connection found. Connect first.")

    provider = _get_provider()
    try:
        data = await provider.fetch_metrics(conn.access_token_enc)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Sync failed: {exc}") from exc

    conn.last_synced_at = datetime.utcnow()
    db.commit()

    return {"status": "synced", "provider": PROVIDER_NAME, "data": data}


@router.get("/connections")
def list_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    connections = (
        db.query(WearableConnection)
        .filter(WearableConnection.user_id == current_user.id)
        .all()
    )
    return {
        "connections": [
            {
                "id": c.id,
                "provider": c.provider,
                "status": c.status,
                "last_synced_at": str(c.last_synced_at) if c.last_synced_at else None,
            }
            for c in connections
        ]
    }
