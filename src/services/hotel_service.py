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
HOTEL_OFFERS_ENDPOINT = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
HOTELS_BY_CITY_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"

# Change API base URL based on environment variable
if AMADEUS_HOST == "production":
    AUTH_ENDPOINT = AUTH_ENDPOINT.replace("test", "api")
    HOTEL_OFFERS_ENDPOINT = HOTEL_OFFERS_ENDPOINT.replace("test", "api")
    HOTELS_BY_CITY_ENDPOINT = HOTELS_BY_CITY_ENDPOINT.replace("test", "api")

class HotelService:
    """
    Amadeus Hotel API service class, using aiohttp to directly call Amadeus API
    """
    
    def __init__(self):
        """
        Initialize Amadeus Hotel API service
        """
        logger.info(f"Initializing Amadeus Hotel API service, client_id: {AMADEUS_CLIENT_ID}, environment: {AMADEUS_HOST}")
        self.client_id = AMADEUS_CLIENT_ID
        self.client_secret = AMADEUS_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = 0
        
    async def _ensure_token(self) -> Optional[str]:
        """
        Ensure access token is valid, refresh if expired
        
        Returns:
            str: Valid access token, or None if retrieval fails
        """
        import time
        current_time = int(time.time())
        
        # Get new token if no token exists or token has expired
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
                            logger.info(f"Access token retrieved successfully, valid for: {expires_in} seconds")
                            return self.access_token
                        else:
                            error_text = await response.text()
                            logger.error(f"Failed to get access token, status code: {response.status}, error: {error_text}")
                            return None
            except Exception as e:
                logger.error(f"Error getting access token: {str(e)}")
                return None
        
        return self.access_token
    
    async def search_hotels_by_city(self, 
                                   city_code: str, 
                                   radius: int = 5,
                                   radius_unit: str = "KM",
                                   chain_codes: Optional[List[str]] = None,
                                   amenities: Optional[List[str]] = None,
                                   ratings: Optional[List[str]] = None,
                                   hotel_source: str = "ALL") -> Dict[str, Any]:
        """
        Search hotels by city code
        
        Args:
            city_code (str): Destination city code or airport code, e.g. 'PAR'
            radius (int): Maximum distance from geographic coordinates, default 5
            radius_unit (str): Distance unit, options: KM, MILE, default KM
            chain_codes (Optional[List[str]]): List of hotel chain codes, each code is 2 uppercase letters
            amenities (Optional[List[str]]): List of amenities, options include: SWIMMING_POOL, SPA, WIFI etc.
            ratings (Optional[List[str]]): Hotel star ratings, options: 1, 2, 3, 4, 5
            hotel_source (str): Hotel source, options: BEDBANK, DIRECTCHAIN, ALL, default ALL
            
        Returns:
            Dict[str, Any]: Hotel search results
        """
        logger.info(f"Searching hotels by city, city code: {city_code}, radius: {radius}{radius_unit}")
        
        # Ensure valid access token
        access_token = await self._ensure_token()
        if not access_token:
            logger.error("Unable to get access token, hotel search failed")
            return {"error": "Unable to get access token", "data": []}
        
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            "cityCode": city_code,
            "radius": radius,
            "radiusUnit": radius_unit,
            "hotelSource": hotel_source
        }
        
        # Add optional parameters
        if chain_codes:
            params["chainCodes"] = ",".join(chain_codes)
        if amenities:
            params["amenities"] = ",".join(amenities)
        if ratings:
            params["ratings"] = ",".join(ratings)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(HOTELS_BY_CITY_ENDPOINT, params=params, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        hotels = result.get('data', [])
                        meta = result.get('meta', {})
                        logger.info(f"Found {len(hotels)} hotels")
                        return {
                            "data": hotels,
                            "meta": meta
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Hotel search failed, status code: {response.status}, error: {error_text}")
                        return {"error": error_text, "data": []}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during hotel search: {error_msg}")
            return {"error": error_msg, "data": []}
    
    async def search_hotel_offers(self, 
                                  hotel_ids: List[str], 
                                  check_in_date: str, 
                                  check_out_date: Optional[str] = None,
                                  adults: int = 1,
                                  room_quantity: int = 1,
                                  price_range: Optional[str] = None,
                                  currency: Optional[str] = None,
                                  board_type: Optional[str] = None,
                                  include_closed: bool = False,
                                  best_rate_only: bool = True) -> Dict[str, Any]:
        """
        Search hotel offers
        
        Args:
            hotel_ids (List[str]): List of hotel IDs, e.g. ["MCLONGHM"]
            check_in_date (str): Check-in date in YYYY-MM-DD format
            check_out_date (Optional[str]): Check-out date in YYYY-MM-DD format, defaults to check-in date + 1 day
            adults (int): Number of adults per room, default 1
            room_quantity (int): Number of rooms, default 1
            price_range (Optional[str]): Price range, e.g. "100-200"
            currency (Optional[str]): Currency code, e.g. "USD"
            board_type (Optional[str]): Board type, options: ROOM_ONLY, BREAKFAST, HALF_BOARD, FULL_BOARD, ALL_INCLUSIVE
            include_closed (bool): Whether to include sold out hotels, default False
            best_rate_only (bool): Whether to return only cheapest offer per hotel, default True
            
        Returns:
            Dict[str, Any]: Hotel offer search results
        """
        logger.info(f"Searching hotel offers, hotel IDs: {hotel_ids}, check-in date: {check_in_date}, check-out date: {check_out_date}")
        
        # Ensure valid access token
        access_token = await self._ensure_token()
        if not access_token:
            logger.error("Unable to get access token, hotel offer search failed")
            return {"error": "Unable to get access token", "data": []}
        
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            "hotelIds": ",".join(hotel_ids),
            "checkInDate": check_in_date,
            "adults": adults,
            "roomQuantity": room_quantity,
            "bestRateOnly": str(best_rate_only).lower()
        }
        
        # Add optional parameters
        if check_out_date:
            params["checkOutDate"] = check_out_date
        if price_range and currency:
            params["priceRange"] = price_range
            params["currency"] = currency
        if board_type:
            params["boardType"] = board_type
        if include_closed:
            params["includeClosed"] = str(include_closed).lower()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(HOTEL_OFFERS_ENDPOINT, params=params, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        hotels = result.get('data', [])
                        logger.info(f"Found {len(hotels)} hotel offers")
                        return {
                            "data": hotels
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Hotel offer search failed, status code: {response.status}, error: {error_text}")
                        return {"error": error_text, "data": []}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during hotel offer search: {error_msg}")
            return {"error": error_msg, "data": []}

# Create service singleton
hotel_service = HotelService()