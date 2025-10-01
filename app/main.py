from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables
from .middleware import SecurityMiddleware, RateLimitMiddleware, CORSMiddleware
from contextlib import asynccontextmanager
from .routers import auth, events, payments, tickets

app = FastAPI(
    title="Event Ticketing System",
    description="Complete event ticketing platform with Paystack integration",
    version="1.0.0"
)

# Add custom middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(CORSMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(payments.router)
app.include_router(tickets.router)

@asynccontextmanager
async def lifespan():
    # Create the database tables
    create_tables()
    yield

@app.get("/")
def root():
    return {
        "message": "Event Ticketing API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}