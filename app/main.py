from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from . import models, schemas, crud
from .database import get_db, create_tables
from .security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .auth import get_current_active_user, get_current_user
from .middleware import SecurityMiddleware, RateLimitMiddleware, CORSMiddleware
from contextlib import asynccontextmanager


app = FastAPI(
    title = "Event Ticketing User Service",
    description = "User management service for the Event Ticketing platform",
    version = "2.0.0"
)

# Add custom middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=50, window_seconds=60)
app.add_middleware(CORSMiddleware)

@asynccontextmanager
async def lifespan():
    # Create the database tables
    create_tables()
    yield

@app.get("/health")
def health_check():
    return {"status": "healthy",
            "service": "User Service", 
            "version": "2.0.0", 
            "security": "JWT enabled"
            }

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_user = crud.create_user(db=db, user=user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/auth/login", response_model=schemas.LoginResponse)
def login_for_access_token(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = crud.authenticate_user(db, user_login.email, user_login.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    return schemas.LoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user)
    )

# Get current user info (protected endpoint)
@app.get("/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

# Get user by ID (protected endpoint)
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a user by ID (requires authentication)"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

# Get multiple users (protected endpoint - admin only for now)
@app.get("/users/", response_model=List[schemas.UserResponse])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
    ):
    """Get multiple users (requires authentication)"""
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# Update current user
@app.put("/auth/me", response_model=schemas.UserResponse)
def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update current user information"""
    current_user_data = schemas.UserResponse.model_validate(current_user)
    db_user = crud.update_user(db, user_id=current_user_data.id, user_update=user_update)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user    

@app.delete("/auth/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Delete current user account (soft delete)"""
    current_user_data = schemas.UserResponse.model_validate(current_user)
    success = crud.delete_user(db, user_id=current_user_data.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete user"
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)