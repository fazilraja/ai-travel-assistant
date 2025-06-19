#!/usr/bin/env python3
"""
Amadeus API Test Script

This script reads environment variables from .env file and tests Amadeus API interfaces
"""

import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError, Location

def main():
    """Test Amadeus API interfaces"""
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
        return
    
    # Initialize Amadeus client
    print("\nInitializing Amadeus client...")
    amadeus = Client(
        client_id=client_id,
        client_secret=client_secret
    )
    
    # Test airport search API
    print("\nTesting airport search API...")
    try:
        response = amadeus.reference_data.locations.get(
            keyword='LON',
            subType=Location.AIRPORT
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
            
    except ResponseError as error:
        print(f"API call failed: {error}")
        print("\nPlease check if your API credentials are correct and network connection is normal")
    
    # Test flight search API
    print("\nTesting flight search API...")
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode='LON',
            destinationLocationCode='PAR',
            departureDate='2025-07-01',
            adults=1
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
            
    except ResponseError as error:
        print(f"Flight search API call failed: {error}")

if __name__ == "__main__":
    main() 