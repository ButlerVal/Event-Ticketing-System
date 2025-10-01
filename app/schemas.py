from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, description="Password must be at least 8 characters long")
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user : UserResponse    

# Event Schemas
class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str
    event_date: datetime
    location: str
    price: Decimal = Field(ge=0)
    capacity: int = Field(gt=0)
    category_id: Optional[int] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    event_date: datetime
    location: str
    price: Decimal
    capacity: int
    tickets_sold: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Ticket Schemas
class TicketResponse(BaseModel):
    id: int
    ticket_code: str
    event_id: int
    status: str
    purchase_date: datetime
    amount_paid: Decimal
    qr_code_path: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Payment Schemas
class PaymentInitiate(BaseModel):
    event_id: int
    email: EmailStr

class PaymentResponse(BaseModel):
    authorization_url: str
    reference: str
    access_code: str

class PaymentVerify(BaseModel):
    reference: str