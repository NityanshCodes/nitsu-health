from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth import ChangePasswordRequest, UpdateProfileRequest, UserResponse
from app.services.auth_service import change_password, get_user_by_id, update_profile
from app.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UpdateProfileRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = update_profile(db, current_user, data)
    return UserResponse.model_validate(user)


@router.patch("/me/password")
def change_password_route(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    change_password(db, current_user, data)
    return {"message": "password updated"}
