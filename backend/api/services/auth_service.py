from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.user import User, UserRole
from utils.auth import get_password_hash, verify_password

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user_data["password"])
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            role=user_data.get("role", UserRole.VIEWER)
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    async def list_users(self) -> List[User]:
        """List all users"""
        return self.db.query(User).all()
    
    async def update_user_role(self, user_id: int, new_role: UserRole) -> Optional[User]:
        """Update user role"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.role = new_role
            self.db.commit()
            self.db.refresh(user)
            return user
        return None
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False
