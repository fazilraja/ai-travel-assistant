#!/usr/bin/env python3
"""
Amadeus Service Test Script

This script tests the AmadeusService implemented using direct API calls
"""

import os
import asyncio
from dotenv import load_dotenv

# Ensure environment variables are loaded first
load_dotenv()

# Import services
from src.services.amadeus_service import amadeus_service
from src.utils.logger import get_logger

# Configure logging
logger = get_logger(__name__)

async def test_search_airports():
    """Test airport search functionality"""
    print("\nTesting airport search functionality...")
    
    # Search for Beijing airport
    results = await amadeus_service.search_airports(keyword="PEK")
    
    if results:
        print(f"Successfully found {len(results)} results:")
        for i, airport in enumerate(results[:3], 1):
            print(f"\nAirport {i}:")
            print(f"  Name: {airport.get('name', 'Unknown')}")
            print(f"  Code: {airport.get('iataCode', 'Unknown')}")
            address = airport.get('address', {})
            print(f"  City: {address.get('cityName', 'Unknown')}")
            print(f"  Country: {address.get('countryName', 'Unknown')}")
        
        if len(results) > 3:
            print(f"\n...and {len(results) - 3} more results")
            
        return True
    else:
        print("No airports found, or API call failed")
        return False

async def test_search_flights():
    """Test flight search functionality"""
    print("\nTesting flight search functionality...")
    
    # Search for flights from Beijing to Shanghai
    result = await amadeus_service.search_flights(
        origin="PEK", 
        destination="SHA", 
        departure_date="2025-07-01",
        adults=1,
        max_results=10
    )
    
    flights = result.get("data", [])
    error = result.get("error")
    
    if error:
        print(f"Flight search failed: {error}")
        return False
    
    if flights:
        print(f"Successfully found {len(flights)} flights:")
        
        dictionaries = result.get("dictionaries", {})
        carriers = dictionaries.get("carriers", {})
        
        for i, flight in enumerate(flights[:2], 1):
            price = flight.get('price', {})
            print(f"\nFlight {i}:")
            print(f"  Price: {price.get('total')} {price.get('currency', 'EUR')}")
            
            itineraries = flight.get('itineraries', [])
            for j, itinerary in enumerate(itineraries):
                segments = itinerary.get('segments', [])
                print(f"  Itinerary {j+1}:")
                
                for k, segment in enumerate(segments):
                    departure = segment.get('departure', {})
                    arrival = segment.get('arrival', {})
                    carrier_code = segment.get('carrierCode', '')
                    carrier_name = carriers.get(carrier_code, carrier_code)
                    flight_number = segment.get('number', '')
                    
                    print(f"    Segment {k+1}: {departure.get('iataCode', '')} → {arrival.get('iataCode', '')}")
                    print(f"    Flight: {carrier_name} ({carrier_code}{flight_number})")
                    print(f"    Departure: {departure.get('at', '').replace('T', ' ')}")
                    print(f"    Arrival: {arrival.get('at', '').replace('T', ' ')}")
        
        if len(flights) > 2:
            print(f"\n...and {len(flights) - 2} more flights")
            
        return True
    else:
        print("No flights found, or API call failed")
        return False

async def test_checkin_links():
    """Test check-in links functionality"""
    print("\nTesting check-in links functionality...")
    
    # Get British Airways check-in links
    links = await amadeus_service.get_flight_checkin_links(airline_code="BA")
    
    if links:
        print(f"Successfully found {len(links)} check-in links:")
        
        for i, link in enumerate(links, 1):
            print(f"\nLink {i}:")
            print(f"  Airline: {link.get('airlineCode', 'Unknown')}")
            print(f"  Link: {link.get('href', 'Unknown')}")
            print(f"  Type: {link.get('type', 'Unknown')}")
            
        return True
    else:
        print("No check-in links found, or API call failed")
        return False

async def main():
    """Main test function"""
    print("Starting test of new AmadeusService...\n")
    
    # Test token acquisition
    print("Getting access token...")
    token = await amadeus_service._ensure_token()
    if token:
        print("Access token obtained successfully!")
    else:
        print("Failed to get access token, test terminated")
        return
    
    # Test each API functionality
    airport_test = await test_search_airports()
    flight_test = await test_search_flights()
    checkin_test = await test_checkin_links()
    
    # Test summary
    print("\nTest Summary:")
    print(f"- Access Token Acquisition: {'Success' if token else 'Failed'}")
    print(f"- Airport Search Functionality: {'Success' if airport_test else 'Failed'}")
    print(f"- Flight Search Functionality: {'Success' if flight_test else 'Failed'}")
    print(f"- Check-in Links Functionality: {'Success' if checkin_test else 'Failed'}")

if __name__ == "__main__":
    asyncio.run(main()) 