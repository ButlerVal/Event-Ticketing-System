from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    organized_events = relationship("Event", back_populates="organizer")
    tickets = relationship("Ticket", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    events = relationship("Event", back_populates="category")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    location = Column(String(255), nullable=False)
    address = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    capacity = Column(Integer, nullable=False)
    tickets_sold = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    organizer_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="events")
    organizer = relationship("User", back_populates="organized_events")
    tickets = relationship("Ticket", back_populates="event")
    payments = relationship("Payment", back_populates="event")

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_code = Column(String(50), unique=True, nullable=False)
    qr_code_data = Column(Text)
    qr_code_path = Column(String(255))
    status = Column(String(20), default='active')
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())
    amount_paid = Column(DECIMAL(10, 2), nullable=False)
    seat_number = Column(String(20))
    special_instructions = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    payment = relationship("Payment", back_populates="ticket")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', 'seat_number', name='unique_user_event_seat'),
    )

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    paystack_reference = Column(String(100), unique=True, nullable=False)
    paystack_access_code = Column(String(100))
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='NGN')
    status = Column(String(20), default='pending')
    payment_method = Column(String(50))
    gateway_response = Column(Text)
    paid_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")
    event = relationship("Event", back_populates="payments")
    ticket = relationship("Ticket", back_populates="payment")