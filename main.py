"""
Lemi Hotel Management System - Backend API
FastAPI application for managing hotel daily summaries.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import init_db
from routes import router as summary_router

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database tables on startup.
    """
    # Startup
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
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not allowed_origins or allowed_origins == [""]:
    # Default origins for development and production
    allowed_origins = [
        "http://localhost:8081",       # Gift's dev server
        "http://localhost:4173",       # Gift's production preview
        "http://localhost:3000",       # Generic frontend dev
        "http://localhost:8080",       # Alternative dev port
        "https://homs-backend-txs8.onrender.com",  # Backend self-reference
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(summary_router)


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
