from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.permission import Permission, UserPermission
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PermissionAssign
from app.api.dependencies import get_current_admin, get_current_user

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Admin creates a new user (superuser, teacher, etc.)"""
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: UserRole = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Get all users with optional role filter"""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password" and value:
            setattr(user, "hashed_password", get_password_hash(value))
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin user"
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/{user_id}/permissions")
async def assign_permission(
    user_id: int,
    permission_data: PermissionAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Assign a permission to a superuser"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != UserRole.SUPERUSER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only assign permissions to superusers"
        )

    permission = db.query(Permission).filter(
        Permission.name == permission_data.permission_name
    ).first()

    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    # Check if already assigned
    existing = db.query(UserPermission).filter(
        UserPermission.user_id == user_id,
        UserPermission.permission_id == permission.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already assigned"
        )

    user_permission = UserPermission(
        user_id=user_id,
        permission_id=permission.id,
        granted_by=current_user.id
    )

    db.add(user_permission)
    db.commit()

    return {"message": "Permission assigned successfully"}


@router.delete("/{user_id}/permissions/{permission_name}")
async def revoke_permission(
    user_id: int,
    permission_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Revoke a permission from a superuser"""
    permission = db.query(Permission).filter(Permission.name == permission_name).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    user_permission = db.query(UserPermission).filter(
        UserPermission.user_id == user_id,
        UserPermission.permission_id == permission.id
    ).first()

    if not user_permission:
        raise HTTPException(status_code=404, detail="Permission not assigned to user")

    db.delete(user_permission)
    db.commit()

    return {"message": "Permission revoked successfully"}
