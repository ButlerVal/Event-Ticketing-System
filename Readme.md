# Event Ticketing System

Complete event ticketing platform with Paystack payment integration.

## Features

- User authentication with JWT
- Event management
- Paystack payment integration with circuit breaker
- QR code ticket generation
- Email notifications
- Rate limiting

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL
- Gmail account with app password

### Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd EventTicketing

2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies

bashpip install -r requirements.txt

4. Set up environment variables

bashcp .env.example .env
# Edit .env with your actual values

5. Run the application

bashuvicorn app.main:app --reload
Visit http://localhost:8000/docs for API documentation.


