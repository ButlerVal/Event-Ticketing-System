from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .. import models, schemas
from ..security import hash_password, verify_password
from typing import Optional

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get a user by ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        Optional[models.User]: The user if found, None otherwise.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]: 
    """Get a user by email.

    Args:
        db (Session): The database session.
        email (str): The email of the user. 

    Returns:
        Optional[models.User]: The user if found, None otherwise.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users.

    Args:
        db (Session): The database session.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.

    Returns:
        List[models.User]: A list of users.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with bcrypt hashing.

    Args:
        db (Session): The database session.
        user (schemas.UserCreate): The user data.

    Raises:
        ValueError: If the email is already registered.

    Returns:
        models.User: The created user.
    """
    existing_user = get_user_by_email(db, user.email)

    if existing_user:
        raise ValueError("Email already registered")
    
    hashed_password = hash_password(user.password)

    db_user = models.User(email=user.email, name=user.name, password_hash=hashed_password)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Email already registered")
    
def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Authenticate a user by email and password.

    Args:
        db (Session): The database session.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        Optional[models.User]: The authenticated user if credentials are valid, None otherwise.
    """
    user = get_user_by_email(db, email)
    if user and verify_password(password, str(user.password_hash)) and user.is_active is True:
        return user
    return None

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update an existing user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to update.
        user_update (schemas.UserUpdate): The updated user data.

    Returns:
        Optional[models.User]: The updated user if found, None otherwise.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Update Failed!")    
    
def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user by ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to delete.

    Returns:
        bool: True if the user was deleted, False if not found.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    try:
        db.delete(db_user)
        db.commit()
        return True  
    except IntegrityError:
        db.rollback()
        return False  