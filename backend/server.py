from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

# Import core components
from backend.core.database import init_database, close_database
from backend.core.cache import init_cache, close_cache

# Import API routers
from backend.api.videos import router as videos_router
from backend.api.users import router as users_router  
from backend.api.comments import router as comments_router
from backend.api.upload import router as upload_router
from backend.api.oauth import router as oauth_router
from backend.api.tfa import router as tfa_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("Starting YouTube Clone API Server...")
    
    try:
        # Initialize database connection
        await init_database()
        logger.info("Database initialized successfully")
        
        # Initialize cache connection
        await init_cache()
        logger.info("Cache initialized successfully")
        
        logger.info("✅ YouTube Clone API Server started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down YouTube Clone API Server...")
    
    try:
        await close_cache()
        await close_database()
        logger.info("✅ Server shutdown completed")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# Create FastAPI app with lifespan management
app = FastAPI(
    title="YouTube Clone API",
    description="Enterprise-grade YouTube clone with ML recommendations",
    version="1.0.0",
    lifespan=lifespan
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Configure appropriately for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@api_router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "YouTube Clone API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@api_router.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "youtube-clone-api",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

# Include API routers
api_router.include_router(videos_router)
api_router.include_router(users_router)
api_router.include_router(comments_router)
api_router.include_router(upload_router)
api_router.include_router(oauth_router)
api_router.include_router(tfa_router)

# Include the API router in the main app
app.include_router(api_router)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )