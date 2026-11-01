import time
from collections import defaultdict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.security import verify_password, create_access_token
from backend.app.models.employee import UserAccount, Employee, EmployeeRole, Role
from backend.app.schemas.schemas import LoginRequest, Token, UserProfile
from backend.app.permissions.rbac import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Rate limiting storage: sliding window 10 attempts per minute
LOGIN_ATTEMPTS = defaultdict(list)
RATE_LIMIT_WINDOW = 60
MAX_ATTEMPTS = 15


def apply_rate_limit(key: str):
    now = time.time()
    valid_attempts = [t for t in LOGIN_ATTEMPTS[key] if now - t < RATE_LIMIT_WINDOW]
    LOGIN_ATTEMPTS[key] = valid_attempts
    if len(valid_attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: too many login attempts. Please wait 60 seconds before retrying."
        )
    LOGIN_ATTEMPTS[key].append(now)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{payload.username}"
    apply_rate_limit(rate_key)

    # Look up by username or email
    user = db.execute(
        select(UserAccount).where(
            (UserAccount.username == payload.username) | (UserAccount.email == payload.username)
        )
    ).scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Get roles
    roles = db.execute(
        select(Role.name)
        .join(EmployeeRole, EmployeeRole.role_id == Role.role_id)
        .where(EmployeeRole.employee_id == user.employee_id)
    ).scalars().all()

    access_token = create_access_token(
        subject=user.user_id,
        claims={"employee_id": user.employee_id, "username": user.username, "roles": list(roles)}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id,
        employee_id=user.employee_id,
        username=user.username,
        roles=list(roles)
    )


@router.get("/me", response_model=UserProfile)
def get_me(current_user: AuthenticatedUser = Depends(get_current_user)):
    emp = current_user.employee
    return UserProfile(
        user_id=current_user.user.user_id,
        employee_id=emp.employee_id,
        username=current_user.user.username,
        email=emp.email,
        full_name=emp.full_name,
        department=emp.department,
        job_title=emp.job_title,
        roles=current_user.roles
    )
