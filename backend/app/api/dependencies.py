from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.permission import Permission, UserPermission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_superuser_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def check_permission(permission_name: str):
    """Dependency factory to check if user has specific permission"""
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Admins have all permissions
        if current_user.role == UserRole.ADMIN:
            return current_user

        # Check if superuser has this specific permission
        if current_user.role == UserRole.SUPERUSER:
            permission = db.query(Permission).filter(
                Permission.name == permission_name
            ).first()

            if permission:
                has_permission = db.query(UserPermission).filter(
                    UserPermission.user_id == current_user.id,
                    UserPermission.permission_id == permission.id
                ).first()

                if has_permission:
                    return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission_name}' required"
        )

    return permission_checker
