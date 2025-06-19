#!/usr/bin/env python3
"""
Amadeus API Direct Call Test Script

Test script for directly calling Amadeus API using aiohttp without SDK, reading credentials from .env file
"""

import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv
from datetime import datetime, timedelta

# API endpoints
AUTH_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"
AIRPORT_SEARCH_ENDPOINT = "https://test.api.amadeus.com/v1/reference-data/locations"
FLIGHT_SEARCH_ENDPOINT = "https://test.api.amadeus.com/v2/shopping/flight-offers"
CHECKIN_LINKS_ENDPOINT = "https://test.api.amadeus.com/v2/reference-data/urls/checkin-links"

async def get_access_token(client_id, client_secret):
    """Get Amadeus API access token"""
    print("Getting access token...")
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AUTH_ENDPOINT, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    access_token = result.get('access_token')
                    expires_in = result.get('expires_in', 0)
                    print(f"Access token obtained successfully! Valid for: {expires_in} seconds")
                    return access_token
                else:
                    error_text = await response.text()
                    print(f"Failed to get access token, status code: {response.status}")
                    print(f"Error details: {error_text}")
                    return None
    except Exception as e:
        print(f"Error getting access token: {str(e)}")
        return None

async def search_airports(access_token, keyword="LON", subtype="AIRPORT"):
    """Search airports"""
    print(f"\nSearching airports (keyword: {keyword})...")
    
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
                    print(f"Found {len(airports)} airports")
                    
                    # Print first 3 results
                    for i, airport in enumerate(airports[:3], 1):
                        print(f"\nAirport {i}:")
                        print(f"  Name: {airport.get('name', 'Unknown')}")
                        print(f"  Code: {airport.get('iataCode', 'Unknown')}")
                        print(f"  Type: {airport.get('subType', 'Unknown')}")
                        address = airport.get('address', {})
                        print(f"  City: {address.get('cityName', 'Unknown')}")
                        print(f"  Country: {address.get('countryName', 'Unknown')}")
                    
                    if len(airports) > 3:
                        print(f"\n...and {len(airports) - 3} more results")
                    
                    return airports
                else:
                    error_text = await response.text()
                    print(f"Airport search failed, status code: {response.status}")
                    print(f"Error details: {error_text}")
                    return []
    except Exception as e:
        print(f"Error during airport search: {str(e)}")
        return []

async def search_flights(access_token, origin="LON", destination="PAR", departure_date=None, adults=1):
    """Search flights"""
    # Use tomorrow's date if not provided
    if not departure_date:
        tomorrow = datetime.now() + timedelta(days=1)
        departure_date = tomorrow.strftime("%Y-%m-%d")
    
    print(f"\nSearching flights (from {origin} to {destination}, date: {departure_date})...")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "max": 10  # Limit results
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(FLIGHT_SEARCH_ENDPOINT, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    flights = result.get('data', [])
                    dictionaries = result.get('dictionaries', {})
                    print(f"Found {len(flights)} flights")
                    
                    # Get carrier information
                    carriers = dictionaries.get('carriers', {})
                    
                    # Print first 2 results
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
                    
                    return flights
                else:
                    error_text = await response.text()
                    print(f"Flight search failed, status code: {response.status}")
                    print(f"Error details: {error_text}")
                    return []
    except Exception as e:
        print(f"Error during flight search: {str(e)}")
        return []

async def get_checkin_links(access_token, airline_code="BA"):
    """Get airline check-in links"""
    print(f"\nGetting airline check-in links (airline code: {airline_code})...")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {"airlineCode": airline_code}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CHECKIN_LINKS_ENDPOINT, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    links = result.get('data', [])
                    print(f"Found {len(links)} check-in links")
                    
                    # Print all results
                    for i, link in enumerate(links, 1):
                        print(f"\nLink {i}:")
                        print(f"  Airline: {link.get('airlineCode', 'Unknown')}")
                        print(f"  Link: {link.get('href', 'Unknown')}")
                        print(f"  Type: {link.get('type', 'Unknown')}")
                    
                    return links
                else:
                    error_text = await response.text()
                    print(f"Failed to get check-in links, status code: {response.status}")
                    print(f"Error details: {error_text}")
                    return []
    except Exception as e:
        print(f"Error getting check-in links: {str(e)}")
        return []

async def batch_test_checkin_links(access_token, airline_code="BA", num_requests=5):
    """Batch test check-in links API"""
    print(f"\nBatch testing check-in links API (number of requests: {num_requests})...")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {"airlineCode": airline_code}
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            task = asyncio.create_task(
                session.get(CHECKIN_LINKS_ENDPOINT, params=params, headers=headers)
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        error_count = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Request {i+1} failed: {str(response)}")
                error_count += 1
            else:
                if response.status == 200:
                    success_count += 1
                else:
                    error_text = await response.text()
                    print(f"Request {i+1} failed, status code: {response.status}")
                    print(f"Error details: {error_text}")
                    error_count += 1
        
        print(f"\nBatch test results: {success_count} successful, {error_count} failed")

async def main():
    """Main function"""
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
    
    # Get access token
    access_token = await get_access_token(client_id, client_secret)
    if not access_token:
        print("Error: Unable to get access token, please check if API credentials are correct")
        return
    
    # Test airport search API
    airports = await search_airports(access_token, keyword="PEK")
    
    # Test flight search API
    flights = await search_flights(access_token, origin="PEK", destination="SHA")
    
    # Test airline check-in links API
    links = await get_checkin_links(access_token, airline_code="BA")
    
    # Batch test check-in links API
    await batch_test_checkin_links(access_token, airline_code="BA", num_requests=5)

if __name__ == "__main__":
    asyncio.run(main()) 