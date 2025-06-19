"""
Hotel Search Agent Module - Complete hotel search agent implementation using OpenAI Agents SDK

This module provides a complete hotel search agent with integrated tools for:
1. Searching hotels by city (basic hotel information)
2. Searching hotel offers with dates and pricing
3. Natural language processing for hotel queries

Usage example:
```python
from hotel_agent import process_hotel_query, create_hotel_agent

# Process a natural language query
result = await process_hotel_query("I need a hotel in London for next week")

# Or create and use the agent directly
agent = create_hotel_agent()
result = await Runner.run(agent, input="Find hotels in Paris")
```
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
load_dotenv()

try:
    from src.services.hotel_service import hotel_service
except ImportError:
    hotel_service = None
    logging.warning("Hotel service not found - some functionality may be limited")

try:
    from src.prompt.hotel_prompts import get_hotel_system_message
except ImportError:
    def get_hotel_system_message(hotel_mapping=None, city_mapping=None):
        return """You are a professional hotel search assistant. Help users find hotels by:
        1. Understanding their location preferences and dates
        2. Using the available tools to search for hotels
        3. Providing clear, helpful information about available options
        
        Always ask for clarification if needed and provide detailed, formatted responses."""

# Configure logging
logger = logging.getLogger(__name__)

# ===== Hotel ID Mapping Dictionary =====
# This mapping is used to convert city names to corresponding hotel IDs
HOTEL_ID_MAPPING = {
    "london": ["MCLONGHM", "HSLONROT"],
    "lon": ["MCLONGHM", "HSLONROT"],
    
    "newyork": ["NYNYCTSC", "NYCNYCHM"],
    "nyc": ["NYNYCTSC", "NYCNYCHM"],
    "new york": ["NYNYCTSC", "NYCNYCHM"],

    "paris": ["PARPARHT", "HSPARPDG"],
    "par": ["PARPARHT", "HSPARPDG"],
    
    "tokyo": ["TYOPACTH", "TYOTYOKH"],
    "tyo": ["TYOPACTH", "TYOTYOKH"],
    
    "beijing": ["PEKPEKFS", "PEKBEKRG"],
    "pek": ["PEKPEKFS", "PEKBEKRG"],
    
    "shanghai": ["SHAPUDHD", "SHAPEKRG"],
    "sha": ["SHAPUDHD", "SHAPEKRG"],
    
    "hongkong": ["HKGHKGSH", "HKGHKGHR"],
    "hkg": ["HKGHKGSH", "HKGHKGHR"],
    "hong kong": ["HKGHKGSH", "HKGHKGHR"],
    
    "singapore": ["SINSINRH", "SINSINFS"],
    "sin": ["SINSINRH", "SINSINFS"],
    
    "bangkok": ["BKKBKKHB", "BKKBKKSH"],
    "bkk": ["BKKBKKHB", "BKKBKKSH"],
    
    "sydney": ["SYDSYDHP", "SYDSYDFS"],
    "syd": ["SYDSYDHP", "SYDSYDFS"],
    
    "dubai": ["DXBDUBCC", "DXBDUBIC"],
    "dxb": ["DXBDUBCC", "DXBDUBIC"],
    
    "losangeles": ["LAXLAXTL", "LAXBVRMC"],
    "lax": ["LAXLAXTL", "LAXBVRMC"],
    
    "los angeles": ["LAXLAXTL", "LAXBVRMC"],
    
    "sanfrancisco": ["SFOSFOLW", "SFOSFOSC"],
    "sfo": ["SFOSFOLW", "SFOSFOSC"],
    "san francisco": ["SFOSFOLW", "SFOSFOSC"],
}

# ===== City Code Mapping Dictionary =====
# This mapping is used to convert city names to corresponding city codes
CITY_CODE_MAPPING = {
    "london": "LON",
    "paris": "PAR",
    "newyork": "NYC",
    "new york": "NYC",
    "tokyo": "TYO",
    "beijing": "PEK",
    "shanghai": "SHA",
    "hongkong": "HKG",
    "hong kong": "HKG",
    "singapore": "SIN",
    "bangkok": "BKK",
    "sydney": "SYD",
    "dubai": "DXB",
    "losangeles": "LAX",
    "los angeles": "LAX",
    "sanfrancisco": "SFO",
    "san francisco": "SFO",
    "berlin": "BER",
    "frankfurt": "FRA",
    "amsterdam": "AMS",
    "rome": "ROM",
    "madrid": "MAD",
    "barcelona": "BCN",
    "moscow": "MOW",
    "chicago": "CHI",
    "washington": "WAS",
    "boston": "BOS",
    "toronto": "YTO",
    "vancouver": "YVR",
    "montreal": "YMQ",
    "milan": "MIL",
    "vienna": "VIE",
}

# ===== Board Type Mapping =====
BOARD_TYPE_MAPPING = {
    "room only": "ROOM_ONLY",
    "breakfast": "BREAKFAST",
    "half board": "HALF_BOARD",
    "full board": "FULL_BOARD",
    "all inclusive": "ALL_INCLUSIVE",
}

# ===== Tool Functions =====

@function_tool
async def search_hotels_by_city(
    city: str,
    radius: int = 5,
    radius_unit: str = "KM",
    amenities: Optional[List[str]] = None,
    ratings: Optional[List[str]] = None
) -> str:
    """
    Search for hotels by city code, returning basic hotel information rather than offers.
    
    Args:
        city: City name or airport code, e.g., 'london' or 'LON'
        radius: Search radius in kilometers (default: 5)
        radius_unit: Radius unit, options: KM, MILE (default: KM)
        amenities: List of amenities, e.g., ['SWIMMING_POOL', 'WIFI']
        ratings: Hotel star ratings, e.g., ['4', '5']
        
    Returns:
        str: Formatted hotel information
    """
    logger.info(f"Search hotels by city: city={city}, radius={radius}{radius_unit}")
    
    if not hotel_service:
        return "Hotel service is not available. Please check your configuration."
    
    # Get city code mapping
    city_key = city.lower().replace(" ", "")
    city_code = CITY_CODE_MAPPING.get(city_key, city.upper())
    
    try:
        # Search hotels
        hotel_results = await hotel_service.search_hotels_by_city(
            city_code=city_code,
            radius=radius,
            radius_unit=radius_unit,
            amenities=amenities,
            ratings=ratings
        )
        
        if "error" in hotel_results:
            return f"Hotel search failed: {hotel_results['error']}"
        
        hotels = hotel_results.get("data", [])
        meta = hotel_results.get("meta", {})
        
        if not hotels:
            return f"No hotels found in city '{city}' ({city_code}). Please try other cities or increase search radius."
        
        # Build readable response
        response = f"Found {len(hotels)} hotels near {city} ({city_code}) within {radius}{radius_unit} radius:\n\n"
        
        # Format each hotel information
        for i, hotel in enumerate(hotels):
            hotel_name = hotel.get("name", "Unknown Hotel")
            hotel_id = hotel.get("hotelId", "Unknown ID")
            chain_code = hotel.get("chainCode", "")
            iata_code = hotel.get("iataCode", "")
            
            # Get geographical location information
            geo_code = hotel.get("geoCode", {})
            latitude = geo_code.get("latitude", "Unknown")
            longitude = geo_code.get("longitude", "Unknown")
            
            # Get address information
            address = hotel.get("address", {})
            country_code = address.get("countryCode", "")
            
            # Get distance information
            distance = hotel.get("distance", {})
            distance_value = distance.get("value", "Unknown")
            distance_unit_val = distance.get("unit", "KM")
            
            response += f"Hotel {i+1}: {hotel_name}\n"
            response += f"ID: {hotel_id}\n"
            response += f"Chain Code: {chain_code}\n"
            response += f"IATA Code: {iata_code}\n"
            response += f"Location: Latitude {latitude}, Longitude {longitude}\n"
            response += f"Country: {country_code}\n"
            response += f"Distance: {distance_value} {distance_unit_val}\n\n"
            
            if i < len(hotels) - 1:
                response += "---\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search_hotels_by_city: {str(e)}")
        return f"An error occurred while searching for hotels: {str(e)}"

@function_tool
async def search_hotels(
    city: str,
    check_in_date: str,
    check_out_date: Optional[str] = None,
    adults: int = 1,
    room_quantity: int = 1,
    price_range: Optional[str] = None,
    currency: Optional[str] = None,
    board_type: Optional[str] = None
) -> str:
    """
    Search for hotels in a specific city with specified check-in and check-out dates.
    
    Args:
        city: City name or airport code, e.g., 'london' or 'LON'
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format, defaults to one day after check-in
        adults: Number of adults per room (default: 1)
        room_quantity: Number of rooms (default: 1)
        price_range: Price range, e.g., '100-200'
        currency: Currency code, e.g., 'USD' or 'EUR'
        board_type: Board type, options: ROOM_ONLY, BREAKFAST, HALF_BOARD, FULL_BOARD, ALL_INCLUSIVE
        
    Returns:
        str: Formatted hotel information
    """
    logger.info(f"Search hotels: city={city}, check_in_date={check_in_date}, check_out_date={check_out_date}")
    
    if not hotel_service:
        return "Hotel service is not available. Please check your configuration."
    
    # Get hotel IDs for the city
    city_key = city.lower().replace(" ", "")
    hotel_ids = HOTEL_ID_MAPPING.get(city_key, [])
    
    if not hotel_ids:
        return f"No hotel information found for city '{city}'. Please use major cities like London, Paris, New York, etc."
    
    # Handle board type
    board_type_processed = None
    if board_type:
        board_type_processed = BOARD_TYPE_MAPPING.get(board_type.lower(), board_type)
    
    try:
        # Default check-out date to one day after check-in
        if not check_out_date:
            check_in_dt = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out_dt = check_in_dt + timedelta(days=1)
            check_out_date = check_out_dt.strftime("%Y-%m-%d")
        
        # Search hotel offers
        hotel_results = await hotel_service.search_hotel_offers(
            hotel_ids=hotel_ids,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            adults=adults,
            room_quantity=room_quantity,
            price_range=price_range,
            currency=currency,
            board_type=board_type_processed
        )
        
        if "error" in hotel_results:
            return f"Hotel search failed: {hotel_results['error']}"
        
        hotels = hotel_results.get("data", [])
        
        if not hotels:
            return f"No hotel offers found matching your criteria. Please try different dates or cities."
        
        # Build readable response
        response = f"Found {len(hotels)} hotels in {city} from {check_in_date} to {check_out_date}:\n\n"
        
        # Format each hotel information
        for i, hotel_data in enumerate(hotels):
            hotel = hotel_data.get("hotel", {})
            hotel_name = hotel.get("name", "Unknown Hotel")
            hotel_id = hotel.get("hotelId", "Unknown ID")
            city_code = hotel.get("cityCode", "")
            
            response += f"Hotel {i+1}: {hotel_name} ({hotel_id})\n"
            response += f"City Code: {city_code}\n"
            
            # Check if offers are available
            available = hotel_data.get("available", False)
            if not available:
                response += "Status: Sold out\n\n"
                continue
            
            # Get offer list
            offers = hotel_data.get("offers", [])
            response += f"Found {len(offers)} offers:\n"
            
            # Format each offer information
            for j, offer in enumerate(offers):
                offer_id = offer.get("id", "Unknown")
                room = offer.get("room", {})
                room_type = room.get("type", "Unknown")
                room_desc = room.get("description", {}).get("text", "No description")
                
                price = offer.get("price", {})
                currency_code = price.get("currency", "EUR")
                total_price = price.get("total", "Unknown")
                
                # Get policy information
                policies = offer.get("policies", {})
                payment_type = policies.get("paymentType", "Unknown")
                cancellation = policies.get("cancellation", {})
                cancellation_desc = cancellation.get("description", {}).get("text", "No cancellation policy information")
                
                response += f"  Offer {j+1}:\n"
                response += f"  - Room Type: {room_type}\n"
                response += f"  - Description: {room_desc[:100]}{'...' if len(room_desc) > 100 else ''}\n"
                response += f"  - Price: {total_price} {currency_code}\n"
                response += f"  - Payment Type: {payment_type}\n"
                response += f"  - Cancellation Policy: {cancellation_desc}\n\n"
            
            if i < len(hotels) - 1:
                response += "---\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search_hotels: {str(e)}")
        return f"An error occurred while searching for hotels: {str(e)}"

# ===== Agent Creation and Processing =====

def create_hotel_agent(model: str = "gpt-4o-mini") -> Agent:
    """
    Create hotel search intelligent assistant agent
    
    Args:
        model: Model name to use (default: gpt-4o-mini)
        
    Returns:
        Agent instance
    """
    # Get system message with hotel ID mapping and city code mapping
    system_message = get_hotel_system_message(
        hotel_mapping=HOTEL_ID_MAPPING,
        city_mapping=CITY_CODE_MAPPING
    )
    
    # Create hotel search assistant agent
    hotel_agent = Agent(
        name="hotel_assistant",
        instructions=system_message,
        model=model,
        tools=[search_hotels_by_city, search_hotels]
    )
    
    logger.info("Successfully created hotel search intelligent assistant agent")
    return hotel_agent

async def process_hotel_query(query: str, model: str = "gpt-4o-mini") -> str:
    """
    Process hotel query request - Use AI agent to extract parameters, then call hotel search API
    
    Args:
        query: User's natural language query
        model: Model name to use
        
    Returns:
        str: Processing result string containing hotel search results
    """
    try:
        logger.info(f"Processing hotel query: {query}")
        
        # Create hotel search assistant
        agent = create_hotel_agent(model=model)
        
        # Use Agent to process query
        result = await Runner.run(agent, input=query)
        
        logger.info("Successfully processed hotel query")
        return result.final_output
        
    except Exception as e:
        logger.error(f"Error processing hotel query: {str(e)}", exc_info=True)
        return f"Error processing hotel query: {str(e)}"

# ===== Additional Utility Functions =====

def get_supported_cities() -> List[str]:
    """
    Get list of supported cities for hotel search
    
    Returns:
        List of supported city names
    """
    return list(CITY_CODE_MAPPING.keys())

def get_supported_board_types() -> List[str]:
    """
    Get list of supported board types
    
    Returns:
        List of supported board type names
    """
    return list(BOARD_TYPE_MAPPING.keys())

# ===== Example Usage =====

if __name__ == "__main__":
    import asyncio
    
    async def example_usage():
        """Example of how to use the hotel agent"""
        
        # Example 1: Process a natural language query
        query1 = "I need a hotel in London for next week from Monday to Wednesday"
        result1 = await process_hotel_query(query1)
        print("Query 1 Result:")
        print(result1)
        print("\n" + "="*50 + "\n")
        
        # Example 2: Another query
        query2 = "Find me hotels in Paris with good ratings"
        result2 = await process_hotel_query(query2)
        print("Query 2 Result:")
        print(result2)
        print("\n" + "="*50 + "\n")
        
        # Example 3: Direct agent usage
        agent = create_hotel_agent()
        result3 = await Runner.run(agent, input="Show me luxury hotels in Tokyo")
        print("Direct Agent Result:")
        print(result3.final_output)
    
    # Run the example
    asyncio.run(example_usage())