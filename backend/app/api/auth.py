from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.student import Student
from app.schemas.user import Token, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint for all users.
    - Admin/Superuser/Teacher: use their username and password
    - Student: username = year+contract_id, password = year+contract_id (default)
    """
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@router.post("/register/admin", response_model=UserResponse)
async def register_admin(
    username: str,
    password: str,
    email: str,
    full_name: str,
    db: Session = Depends(get_db)
):
    """
    Initial admin registration endpoint.
    This should be called only once to create the first admin.
    In production, this endpoint should be protected or disabled after first use.
    """
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin already exists. Use admin panel to create more users."
        )

    # Check if username exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=UserRole.ADMIN,
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
