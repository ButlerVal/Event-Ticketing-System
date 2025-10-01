# 🎟️ Event Ticketing System

A complete, production-ready event ticketing platform built with FastAPI, featuring Paystack payment integration, QR code generation, email notifications, and comprehensive security features.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Security Features](#security-features)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Core Functionality
- **User Management**: Complete authentication system with JWT tokens
- **Event Management**: Create, list, and manage events with capacity tracking
- **Payment Processing**: Secure Paystack integration with circuit breaker pattern
- **Ticket Generation**: Automatic QR code generation for tickets
- **Email Notifications**: Automated ticket delivery via email
- **Rate Limiting**: Built-in API rate limiting protection
- **Security Headers**: Comprehensive security middleware

### Technical Features
- RESTful API design
- PostgreSQL database with SQLAlchemy ORM
- Bcrypt password hashing
- JWT token-based authentication
- Circuit breaker pattern for payment gateway resilience
- Comprehensive test coverage with pytest
- CORS middleware for frontend integration
- Request logging and monitoring

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.116.1
- **Database**: PostgreSQL with SQLAlchemy 2.0.43
- **Authentication**: JWT (python-jose 3.5.0) + Bcrypt (4.3.0)
- **Payment Gateway**: Paystack API
- **QR Codes**: qrcode 8.2 + pyzbar
- **Email**: SMTP (smtplib)
- **Testing**: pytest 8.4.2 + pytest-asyncio
- **Server**: Uvicorn 0.35.0
- **Production**: Gunicorn with Uvicorn workers

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** (tested with 3.13.7)
- **PostgreSQL 12+** (or access to a PostgreSQL database)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### External Services Required

1. **PostgreSQL Database**
   - Local installation OR cloud service (Render, Heroku, AWS RDS, etc.)

2. **Paystack Account**
   - Sign up at [paystack.com](https://paystack.com)
   - Get your test/live API keys from the dashboard

3. **Gmail Account** (or SMTP-enabled email)
   - For sending ticket emails
   - Enable "App Passwords" for Gmail:
     - Go to Google Account → Security
     - Enable 2-Factor Authentication
     - Generate App Password under "App passwords"

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd EventTicketing
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you encounter issues with `psycopg2`, try:
```bash
pip install psycopg2-binary
```

### Step 4: Set Up PostgreSQL Database

**Option A: Local PostgreSQL**

1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)

2. Create a database:
```sql
CREATE DATABASE event_ticketing;
CREATE USER event_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE event_ticketing TO event_user;
```

3. Your DATABASE_URL will be:
```
postgresql://event_user:your_secure_password@localhost:5432/event_ticketing
```

**Option B: Render PostgreSQL (Free)**

1. Go to [render.com](https://render.com)
2. Create a new PostgreSQL database
3. Copy the "External Database URL"

**Option C: Other Cloud Providers**
- Heroku Postgres
- AWS RDS
- Supabase
- ElephantSQL

### Step 5: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your actual values:

```env
# Database - REQUIRED
DATABASE_URL=postgresql://user:password@host:5432/database

# JWT Secret - REQUIRED (generate a secure random string)
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters-long

# Paystack Keys - REQUIRED
PAYSTACK_SECRET_KEY=sk_test_your_secret_key_here
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key_here

# Email Configuration - REQUIRED
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# Frontend URL - OPTIONAL (defaults to localhost:3000)
FRONTEND_URL=http://localhost:3000
```

**⚠️ Important Security Notes:**

- **JWT_SECRET_KEY**: Generate using Python:
  ```python
  import secrets
  print(secrets.token_urlsafe(32))
  ```

- **SMTP_PASSWORD**: For Gmail, use an App Password (NOT your regular password)

- **Never commit `.env` to version control** (already in `.gitignore`)

## 🏃 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### Production Mode

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Verify Installation

1. **Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status":"healthy"}`

2. **API Root**:
   ```bash
   curl http://localhost:8000/
   ```
   Expected: JSON with API info

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access the auto-generated API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Interactive API explorer
  - Test endpoints directly in browser
  - View request/response schemas

- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  - Alternative documentation format
  - Better for reading/reference

### API Endpoints Overview

#### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info (requires auth)

#### Events (`/events`)
- `POST /events/` - Create event (requires auth)
- `GET /events/` - List all events (public)
- `GET /events/{event_id}` - Get event details (public)

#### Payments (`/payments`)
- `POST /payments/initialize` - Initialize payment (requires auth)
- `GET /payments/verify/{reference}` - Verify payment (requires auth)

#### Tickets (`/tickets`)
- `GET /tickets/my-tickets` - Get user's tickets (requires auth)
- `GET /tickets/{ticket_code}` - Get ticket by code (public)

### Authentication Flow

1. Register a user or login to get a token
2. Include token in subsequent requests:
   ```
   Authorization: Bearer <your_jwt_token>
   ```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report: Open `htmlcov/index.html` in your browser

### Run Specific Test Files

```bash
pytest tests/test_auth.py
pytest tests/test_events.py
pytest tests/test_payments.py
```

### Test Structure

- `tests/test_auth.py` - Authentication endpoints
- `tests/test_events.py` - Event management
- `tests/test_payments.py` - Payment processing
- `tests/test_tickets.py` - Ticket operations
- `tests/test_services.py` - Service layer (QR, email, circuit breaker)

## 🚀 Deployment

### Deploy to Render

1. **Create `render.yaml`** (already included)

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repo
   - Render auto-detects settings from `render.yaml`

4. **Set Environment Variables** in Render dashboard:
   - DATABASE_URL (from Render PostgreSQL)
   - JWT_SECRET_KEY
   - PAYSTACK_SECRET_KEY
   - PAYSTACK_PUBLIC_KEY
   - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
   - FRONTEND_URL

5. **Deploy**: Render automatically builds and deploys

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set JWT_SECRET_KEY=your-secret-key
heroku config:set PAYSTACK_SECRET_KEY=your-paystack-key
# ... set other variables

# Deploy
git push heroku main
```

### Deploy to Railway

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

3. Add PostgreSQL and set environment variables in Railway dashboard

## 📁 Project Structure

```
EventTicketing/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection & session
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── security.py          # Password hashing & JWT functions
│   ├── auth.py              # Authentication dependencies
│   ├── middleware.py        # Custom middleware (security, CORS, rate limiting)
│   ├── cruds/               # Database CRUD operations
│   │   ├── users.py
│   │   ├── events.py
│   │   ├── payments.py
│   │   └── tickets.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   ├── events.py
│   │   ├── payments.py
│   │   └── tickets.py
│   └── services/            # External service integrations
│       ├── paystack.py      # Paystack payment gateway
│       ├── qr_service.py    # QR code generation
│       └── email_service.py # Email notifications
├── tests/                   # Test suite
│   ├── conftest.py          # Test configuration & fixtures
│   ├── test_auth.py
│   ├── test_events.py
│   ├── test_payments.py
│   ├── test_tickets.py
│   └── test_services.py
├── qr_codes/                # Generated QR codes (created at runtime)
├── .env.example             # Environment variables template
├── .gitignore
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment configuration
├── runtime.txt              # Python version
└── README.md
```

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication with expiration
- **Bcrypt Hashing**: Secure password storage with 12 rounds
- **Token Validation**: Middleware validates tokens on protected routes

### API Security
- **Rate Limiting**: 100 requests per 60 seconds per IP
- **CORS Protection**: Configurable allowed origins
- **Security Headers**: 
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security

### Payment Security
- **Circuit Breaker**: Prevents cascade failures
- **Reference Validation**: Unique transaction references
- **Status Tracking**: Payment state management

### Data Security
- **SQL Injection Protection**: SQLAlchemy ORM parameterization
- **Input Validation**: Pydantic schema validation
- **Environment Variables**: Sensitive data not in code

## 🐛 Troubleshooting

### Database Connection Issues

**Problem**: `DATABASE_URL environment variable not set`

**Solution**:
```bash
# Verify .env file exists and contains DATABASE_URL
cat .env | grep DATABASE_URL

# Reload environment variables
source .env  # Linux/Mac
# or restart terminal
```

**Problem**: `psycopg2` installation fails

**Solution**:
```bash
# Install binary version instead
pip install psycopg2-binary
```

### Email Sending Issues

**Problem**: `SMTPAuthenticationError`

**Solution**:
- For Gmail, use an App Password, not your regular password
- Enable 2FA first, then generate App Password
- Ensure SMTP_USER and SMTP_PASSWORD are correct in `.env`

**Problem**: Emails not arriving

**Solution**:
- Check spam folder
- Verify SMTP credentials
- Test with a simple SMTP client
- Check Gmail "Less secure apps" settings (if not using App Password)

### Paystack Integration Issues

**Problem**: `Payment initialization failed`

**Solution**:
- Verify PAYSTACK_SECRET_KEY in `.env`
- Check if using test keys (`sk_test_...`) for development
- Ensure amount is in correct currency (Naira for Nigeria)
- Check Paystack dashboard for API status

**Problem**: `Circuit breaker is OPEN`

**Solution**:
- Wait 60 seconds for circuit breaker to reset
- Check Paystack API status
- Verify network connectivity

### QR Code Issues

**Problem**: QR codes not generating

**Solution**:
```bash
# Ensure qr_codes directory exists and is writable
mkdir -p qr_codes
chmod 755 qr_codes
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
# Linux/Mac:
lsof -i :8000
kill -9 <PID>

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port:
uvicorn app.main:app --port 8001
```

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📧 Support

For issues, questions, or contributions:

1. Check existing issues in the repository
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version)

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- Paystack for payment processing
- All open-source contributors

---

**Happy Coding! 🚀**