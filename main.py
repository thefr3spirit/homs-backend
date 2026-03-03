"""
Lemi Hotel Management System - Backend API
FastAPI application for managing hotel daily summaries.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command

from database import init_db
from routes import router as summary_router
from routes.auth import router as auth_router
from routes.customers import router as customers_router
from routes.customer_balance import router as customer_balance_router
from routes.rooms import router as rooms_router
from routes.bookings import router as bookings_router
from routes.payments import router as payments_router
from routes.admin import router as admin_router

# Load environment variables
load_dotenv()


def run_migrations():
    """Run Alembic migrations on startup."""
    try:
        print("🔄 Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully")
    except Exception as e:
        print(f"⚠️  Migration warning: {e}")
        # Don't fail startup if migrations have issues
        # This allows the app to start even if migrations were already run


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Runs migrations and initializes database tables on startup.
    """
    # Startup
    print("🚀 Starting Lemi Hotel Management System...")
    run_migrations()
    print("🚀 Initializing database...")
    init_db()
    print("✅ Database initialized successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=os.getenv("APP_NAME", "Lemi Hotel Management System"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="""
    Backend API for Lemi Hotel Management System.
    
    ## Features
    * Submit daily hotel summaries from desktop counter app
    * Retrieve today's summary
    * View historical summaries
    * Query summaries by date or date range
    
    ## Data Flow
    Desktop Counter App → POST /summary → PostgreSQL (Supabase) → GET /summary/* → Mobile Owner App
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_str:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
else:
    # Default origins for development and production
    allowed_origins = [
        "http://localhost:8081",       # Gift's dev server
        "http://localhost:4173",       # Gift's production preview
        "http://localhost:5173",       # Vite default dev
        "http://localhost:3000",       # Generic frontend dev
        "http://localhost:8080",       # Alternative dev port
        "https://hotel-operations-hub.vercel.app",  # Gift's production PWA
    ]

print(f"🌐 CORS enabled for origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Register routers
app.include_router(summary_router)
app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(customer_balance_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
app.include_router(payments_router)
app.include_router(admin_router)
app.include_router(auth_router, prefix="/auth", tags=["authentication"])


@app.get("/", tags=["health"])
def root():
    """Root endpoint - API health check."""
    return {
        "status": "online",
        "message": "Lemi Hotel Management System API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "backend-api"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )
