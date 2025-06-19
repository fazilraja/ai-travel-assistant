import os
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from src.utils.logger import get_logger

# Configure logging
logger = get_logger(__name__)

# We don't need to reload the .env file here since it's already loaded in main.py
# But for module independence, we still get environment variables once

# Check and log key environment variables
amadeus_client_id = os.getenv("AMADEUS_CLIENT_ID")
amadeus_client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
amadeus_host = os.getenv("AMADEUS_HOST", "test")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Log environment variable status
logger.info(f"Settings loaded with AMADEUS_CLIENT_ID: {amadeus_client_id}")
logger.info(f"Settings loaded with AMADEUS_HOST: {amadeus_host}")

if not amadeus_client_id or not amadeus_client_secret:
    logger.warning("Amadeus API keys not set. Please ensure AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET are defined in .env file.")

if not openai_api_key:
    logger.warning("OpenAI API key not set. Please ensure OPENAI_API_KEY is defined in .env file.")

class Settings:
    # Amadeus API configuration
    AMADEUS_CLIENT_ID = amadeus_client_id
    AMADEUS_CLIENT_SECRET = amadeus_client_secret
    AMADEUS_HOST = amadeus_host  # Use test environment by default
    
    # OpenAI API configuration
    OPENAI_API_KEY = openai_api_key
    
    # Application configuration
    APP_NAME = "Travel Assistant API"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Travel Assistant backend API, providing flight search and AI chat services"

# Create settings instance
settings = Settings()

# Keep original variable names for backward compatibility
AMADEUS_CLIENT_ID = settings.AMADEUS_CLIENT_ID
AMADEUS_CLIENT_SECRET = settings.AMADEUS_CLIENT_SECRET
AMADEUS_HOST = settings.AMADEUS_HOST
OPENAI_API_KEY = settings.OPENAI_API_KEY
APP_NAME = settings.APP_NAME
APP_VERSION = settings.APP_VERSION
APP_DESCRIPTION = settings.APP_DESCRIPTION