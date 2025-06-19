from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import settings
from src.config.settings import APP_NAME, APP_VERSION, APP_DESCRIPTION
from src.routes.flight_routes import router as flight_router
from src.routes.hotel_routes import router as hotel_router
from src.routes.openai_routes import router as openai_router
from src.routes.agent_routes import router as agent_router

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    # Check if critical environment variables exist
    amadeus_client_id = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    
    if not amadeus_client_id or not amadeus_client_secret:
        print(f"Warning: Amadeus API credentials incomplete, client_id={amadeus_client_id}")
    
    app = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
    )
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Should specify actual domains in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    app.include_router(flight_router, prefix="/api/flights", tags=["flights"])
    app.include_router(hotel_router, prefix="/api/hotels", tags=["hotels"])
    app.include_router(openai_router, prefix="/api/openai", tags=["openai"])
    app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
    
    @app.get("/", tags=["health"])
    async def health_check():
        """Health check endpoint"""
        return {"status": "ok", "message": "Service is running normally"}
    
    return app