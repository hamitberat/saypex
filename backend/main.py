"""
Main FastAPI application entry point for Vercel deployment
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import os

from database.postgres import DatabaseManager, get_db
from database.models import Base
from api.users import router as users_router
from api.videos import router as videos_router

app = FastAPI(
    title="Oultic Video Platform API",
    description="A modern video platform backend built with FastAPI and PostgreSQL",
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(videos_router, prefix="/api/videos", tags=["videos"])

@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        is_connected = await DatabaseManager.check_connection()
        if not is_connected:
            raise HTTPException(status_code=503, detail="Database connection failed")
        
        return {
            "status": "healthy",
            "message": "Lotic API is running",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        await DatabaseManager.create_tables()
        print("✅ Database tables initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")

# For Vercel compatibility
def handler(request, context):
    return app(request, context)