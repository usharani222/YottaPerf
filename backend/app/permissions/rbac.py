from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.employee import UserAccount, Employee, EmployeeRole, Role

security = HTTPBearer(auto_error=False)


class AuthenticatedUser:
    def __init__(self, user_account: UserAccount, employee: Employee, roles: List[str]):
        self.user = user_account
        self.employee = employee
        self.roles = roles

    @property
    def user_id(self) -> str:
        return self.user.user_id

    @property
    def employee_id(self) -> str:
        return self.employee.employee_id

    @property
    def is_admin(self) -> bool:
        return "ADMIN" in self.roles

    @property
    def is_hr(self) -> bool:
        return "HR_PARTNER" in self.roles or self.is_admin

    @property
    def is_manager(self) -> bool:
        return "MANAGER" in self.roles or self.is_admin

    @property
    def is_it_ops(self) -> bool:
        return "IT_OPS" in self.roles or self.is_admin


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> AuthenticatedUser:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        import jwt
        from backend.app.core.config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    user_acc = db.execute(select(UserAccount).where(UserAccount.user_id == user_id)).scalar_one_or_none()
    if not user_acc or not user_acc.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    emp = db.execute(select(Employee).where(Employee.employee_id == user_acc.employee_id)).scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Associated employee record not found")

    # Fetch roles
    user_roles = db.execute(
        select(Role.name)
        .join(EmployeeRole, EmployeeRole.role_id == Role.role_id)
        .where(EmployeeRole.employee_id == emp.employee_id)
    ).scalars().all()

    return AuthenticatedUser(user_account=user_acc, employee=emp, roles=list(user_roles))


def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.is_admin:
            return current_user
        if not any(role in current_user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {allowed_roles}"
            )
        return current_user
    return role_checker
