from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from . import schemas
from .cruds import users as user_crud
from .database import get_db
from .security import verify_token

# HTTP Bearer token scheme
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.UserResponse:
    """Get current user from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify token
        token_data = verify_token(token)
        if token_data is None:
            raise credentials_exception
        
        # Get user from database
        user = user_crud.get_user_by_email(db, email=token_data["email"])
        if user is None:
            raise credentials_exception
        
        # Check if user is active
        if user.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        return user
        
    except JWTError:
        raise credentials_exception

def get_current_active_user(
    current_user: schemas.UserResponse = Depends(get_current_user)
) -> schemas.UserResponse:
    """Get current active user (additional validation)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user