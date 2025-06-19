import os
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from src.config.settings import AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET, AMADEUS_HOST
from src.utils.logger import get_logger

# Configure logging
logger = get_logger(__name__)

# API endpoints
AUTH_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"
AIRPORT_SEARCH_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations"
FLIGHT_SEARCH_ENDPOINT = "https://test.api.amadeus.com/v2/shopping/flight-offers"
CHECKIN_LINKS_ENDPOINT = "https://test.api.amadeus.com/v2/reference-data/urls/checkin-links"

# Change API base URL based on environment variable
if AMADEUS_HOST == "production":
    AUTH_ENDPOINT = AUTH_ENDPOINT.replace("test", "api")
    AIRPORT_SEARCH_ENDPOINT = AIRPORT_SEARCH_ENDPOINT.replace("test", "api")
    FLIGHT_SEARCH_ENDPOINT = FLIGHT_SEARCH_ENDPOINT.replace("test", "api")
    CHECKIN_LINKS_ENDPOINT = CHECKIN_LINKS_ENDPOINT.replace("test", "api")

class AmadeusService:
    """
    Amadeus API service class, using aiohttp to directly call Amadeus API
    """
    
    def __init__(self):
        """
        Initialize Amadeus API service
        """
        logger.info(f"Initializing Amadeus API service, client_id: {AMADEUS_CLIENT_ID}, environment: {AMADEUS_HOST}")
        self.client_id = AMADEUS_CLIENT_ID
        self.client_secret = AMADEUS_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = 0
        
    async def _ensure_token(self) -> Optional[str]:
        """
        Ensure access token is valid, refresh if expired
        
        Returns:
            str: Valid access token, or None if failed to obtain
        """
        import time
        current_time = int(time.time())
        
        # Get new token if none exists or is expired
        if not self.access_token or current_time >= self.token_expires_at:
            logger.info("Getting new Amadeus API access token")
            
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(AUTH_ENDPOINT, headers=headers, data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            self.access_token = result.get('access_token')
                            expires_in = result.get('expires_in', 1800)  # Default 30 minutes
                            self.token_expires_at = current_time + expires_in - 60  # Refresh 60 seconds early
                            logger.info(f"Access token obtained successfully, valid for: {expires_in} seconds")
                            return self.access_token
                        else:
                            error_text = await response.text()
                            logger.error(f"Failed to get access token, status code: {response.status}, error: {error_text}")
                            return None
            except Exception as e:
                logger.error(f"Error getting access token: {str(e)}")
                return None
        
        return self.access_token
    
    async def search_airports(self, keyword: str, subtype: str = "AIRPORT") -> List[Dict[str, Any]]:
        """
        Search airports by keyword
        
        Args:
            keyword (str): Search keyword
            subtype (str): Location type, defaults to AIRPORT
            
        Returns:
            List[Dict[str, Any]]: List of airport search results
        """
        logger.info(f"Searching airports, keyword: {keyword}, type: {subtype}")
        
        # Ensure valid access token
        access_token = await self._ensure_token()
        if not access_token:
            logger.error("Unable to get access token, airport search failed")
            return []
        
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            "keyword": keyword,
            "subType": subtype
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(AIRPORT_SEARCH_ENDPOINT, params=params, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        airports = result.get('data', [])
                        logger.info(f"Found {len(airports)} airports")
                        return airports
                    else:
                        error_text = await response.text()
                        logger.error(f"Airport search failed, status code: {response.status}, error: {error_text}")
                        return []
        except Exception as e:
            logger.error(f"Error during airport search: {str(e)}")
            return []
    
    async def search_flights(self, origin: str, destination: str, departure_date: str, 
                            adults: int = 1, max_results: int = 3) -> Dict[str, Any]:
        """
        Search flights
        
        Args:
            origin (str): Origin location code (e.g., 'MAD')
            destination (str): Destination location code (e.g., 'BCN')
            departure_date (str): Departure date (format: 'YYYY-MM-DD')
            adults (int): Number of adult passengers
            max_results (int): Maximum number of results
            
        Returns:
            Dict[str, Any]: Flight search results
        """
        logger.info(f"Searching flights from {origin} to {destination}, date: {departure_date}, adults: {adults}, max results: {max_results}")
        
        # Ensure valid access token
        access_token = await self._ensure_token()
        if not access_token:
            logger.error("Unable to get access token, flight search failed")
            return {"error": "Unable to get access token", "data": []}
        
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(FLIGHT_SEARCH_ENDPOINT, params=params, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        flights = result.get('data', [])
                        dictionaries = result.get('dictionaries', {})
                        logger.info(f"Found {len(flights)} flights")
                        return {
                            "data": flights,
                            "dictionaries": dictionaries
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Flight search failed, status code: {response.status}, error: {error_text}")
                        return {"error": error_text, "data": []}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during flight search: {error_msg}")
            return {"error": error_msg, "data": []}
    
    async def get_flight_checkin_links(self, airline_code: str) -> List[Dict[str, Any]]:
        """
        Get airline check-in links
        
        Args:
            airline_code (str): Airline code
            
        Returns:
            List[Dict[str, Any]]: List of check-in link information
        """
        logger.info(f"Getting airline check-in links, airline code: {airline_code}")
        
        # Ensure valid access token
        access_token = await self._ensure_token()
        if not access_token:
            logger.error("Unable to get access token, check-in link retrieval failed")
            return []
        
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {"airlineCode": airline_code}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(CHECKIN_LINKS_ENDPOINT, params=params, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        links = result.get('data', [])
                        logger.info(f"Found {len(links)} check-in links")
                        return links
                    else:
                        error_text = await response.text()
                        logger.error(f"Check-in link retrieval failed, status code: {response.status}, error: {error_text}")
                        return []
        except Exception as e:
            logger.error(f"Error getting check-in links: {str(e)}")
            return []

# Create service singleton
amadeus_service = AmadeusService()