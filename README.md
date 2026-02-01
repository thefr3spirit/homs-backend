# Lemi Hotel Management System - Backend API

FastAPI backend for storing and serving daily hotel summary data.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env`
   - Update `DATABASE_URL` with your Supabase PostgreSQL credentials

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

5. **API Documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /summary
Submit daily hotel summary data.

**Request Body:**
```json
{
  "date": "2026-01-31",
  "rooms_total": 20,
  "rooms_occupied": 8,
  "rooms_available": 12,
  "cash_collected": 350000,
  "momo_collected": 120000,
  "total_collected": 470000,
  "expected_balance": 470000,
  "expenses_logged": 20000
}
```

### GET /summary/today
Retrieve today's summary.

### GET /summary/history?limit=30
Retrieve historical summaries.

## Project Structure

```
backend/
├── database/       # Database connection and session management
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic schemas for validation
├── routes/         # API endpoints
├── services/       # Business logic
├── main.py         # FastAPI application entry point
├── requirements.txt
└── .env.example
```
