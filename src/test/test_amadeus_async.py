#!/usr/bin/env python3
"""
Amadeus API Async Test Script

This script uses async functions to test Amadeus API, simulating real application usage patterns
"""

import os
import asyncio
from dotenv import load_dotenv
from amadeus import Client, ResponseError, Location

# Global client
amadeus = None

async def init_client():
    """Initialize Amadeus client"""
    global amadeus
    
    # Load environment variables
    print("Loading environment variables...")
    load_dotenv()
    
    # Get API credentials
    client_id = os.getenv("AMADEUS_CLIENT_ID")
    client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    
    print(f"Amadeus Client ID: {client_id}")
    print(f"Amadeus Client Secret: {'*' * len(client_secret) if client_secret else 'Not set'}")
    
    if not client_id or not client_secret:
        print("Error: Amadeus API credentials not found, please ensure .env file contains AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET")
        return False
    
    # Initialize client
    print("\nInitializing Amadeus client...")
    try:
        amadeus = Client(
            client_id=client_id,
            client_secret=client_secret
        )
        return True
    except Exception as e:
        print(f"Client initialization failed: {e}")
        return False

async def search_airports(keyword="LON", subtype=Location.AIRPORT):
    """Search airports"""
    print(f"\nTesting airport search API (keyword={keyword})...")
    
    if not amadeus:
        print("Error: Amadeus client not initialized")
        return
    
    try:
        # Note: amadeus library itself is not async, but we call it within an async function
        response = amadeus.reference_data.locations.get(
            keyword=keyword,
            subType=subtype
        )
        
        print(f"API call successful! Found {len(response.data)} results:")
        
        # Print first 3 results
        for i, item in enumerate(response.data[:3], 1):
            print(f"\nResult {i}:")
            print(f"  Type: {item.get('subType', 'Unknown')}")
            print(f"  Name: {item.get('name', 'Unknown')}")
            print(f"  Code: {item.get('iataCode', 'Unknown')}")
            print(f"  City: {item.get('address', {}).get('cityName', 'Unknown')}")
            print(f"  Country: {item.get('address', {}).get('countryName', 'Unknown')}")
        
        if len(response.data) > 3:
            print(f"\n...and {len(response.data) - 3} other results")
            
        return response.data
            
    except ResponseError as error:
        print(f"API call failed: {error}")
        print("\nPlease check if your API credentials are correct and network connection is normal")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None

async def search_flights(origin="LON", destination="PAR", departure_date="2025-07-01", adults=1):
    """Search flights"""
    print(f"\nTesting flight search API (from {origin} to {destination})...")
    
    if not amadeus:
        print("Error: Amadeus client not initialized")
        return
    
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=adults
        )
        
        print(f"API call successful! Found {len(response.data)} flights:")
        
        # Print first 2 results
        for i, flight in enumerate(response.data[:2], 1):
            print(f"\nFlight {i}:")
            print(f"  Price: {flight.get('price', {}).get('total')} {flight.get('price', {}).get('currency', 'EUR')}")
            
            itineraries = flight.get('itineraries', [])
            for j, itinerary in enumerate(itineraries):
                segments = itinerary.get('segments', [])
                print(f"  Segment {j+1}:")
                
                for k, segment in enumerate(segments):
                    departure = segment.get('departure', {})
                    arrival = segment.get('arrival', {})
                    carrier = segment.get('carrierCode', '')
                    flight_number = segment.get('number', '')
                    
                    print(f"    {departure.get('iataCode', '')} → {arrival.get('iataCode', '')}")
                    print(f"    Flight: {carrier}{flight_number}")
                    print(f"    Departure: {departure.get('at', '')}")
                    print(f"    Arrival: {arrival.get('at', '')}")
        
        if len(response.data) > 2:
            print(f"\n...and {len(response.data) - 2} other flights")
            
        return response.data
            
    except ResponseError as error:
        print(f"Flight search API call failed: {error}")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None

async def main():
    """Main test function"""
    # Initialize client
    if not await init_client():
        return
    
    # Test airport search
    airports = await search_airports(keyword="BEI")  # Beijing
    
    # If airport search successful, test flight search
    if airports and len(airports) > 0:
        # Use first airport as origin
        origin = airports[0].get('iataCode')
        await search_flights(origin=origin, destination="SHA")  # Shanghai
    else:
        # Use default values for flight search test
        await search_flights(origin="PEK", destination="SHA", departure_date="2025-07-15")

if __name__ == "__main__":
    asyncio.run(main()) 