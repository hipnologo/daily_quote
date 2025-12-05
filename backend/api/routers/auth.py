from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

from database import get_database
from models.user import User, UserRole
from services.auth_service import AuthService
from utils.auth import create_access_token, verify_token

router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole = UserRole.VIEWER

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class LoginResponse(BaseModel):
    user: UserResponse
    token: Token

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_database)
):
    """Register a new admin user"""
    auth_service = AuthService(db)
    
    # Check if user already exists
    if await auth_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if await auth_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await auth_service.create_user(user_data.dict())
    return user

@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database)
):
    """Authenticate user and return JWT token"""
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
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
    
    # Update last login
    await auth_service.update_last_login(user.id)
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "user": user,
        "token": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutes
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(verify_token)
):
    """Get current user information"""
    return current_user

@router.post("/logout")
async def logout(
    current_user: User = Depends(verify_token)
):
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: Session = Depends(get_database),
    current_user: User = Depends(verify_token)
):
    """List all users (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    auth_service = AuthService(db)
    users = await auth_service.list_users()
    return users

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_database),
    current_user: User = Depends(verify_token)
):
    """Update user role (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    auth_service = AuthService(db)
    user = await auth_service.update_user_role(user_id, new_role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(verify_token)
):
    """Deactivate user (admin only)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    auth_service = AuthService(db)
    success = await auth_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}
