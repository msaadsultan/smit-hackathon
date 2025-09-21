from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..db import get_db
from . import security
from .models import UserCreate, UserResponse, Token, UserRole
from .security import get_current_active_user, check_role

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_role(UserRole.ADMIN))
):
    db_user = security.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = security.get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = security.get_user(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_active_user)):
    return current_user