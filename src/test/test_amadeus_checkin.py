#!/usr/bin/env python3
"""
Amadeus Check-in Links API Test Script

Based on user-provided examples, uses environment variables and focuses on check-in links API
"""

import os
import asyncio
import aiohttp
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials
CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# API endpoints
AUTH_ENDPOINT = "https://test.api.amadeus.com/v1/security/oauth2/token"
CHECKIN_LINKS_ENDPOINT = "https://test.api.amadeus.com/v2/reference-data/urls/checkin-links"

def get_access_token():
    """Get Amadeus API access token"""
    print(f"Getting access token... (Client ID: {CLIENT_ID})")
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    try:
        response = requests.post(AUTH_ENDPOINT, headers=headers, data=data)
        
        if response.status_code == 200:
            result = response.json()
            access_token = result['access_token']
            expires_in = result.get('expires_in', 0)
            print(f"Access token retrieved successfully! Valid for: {expires_in} seconds")
            return access_token
        else:
            print(f"Failed to get access token, status code: {response.status_code}")
            print(f"Error details: {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred while getting access token: {str(e)}")
        return None

async def test_checkin_links(access_token, airline_code="BA", num_requests=20):
    """Test check-in links API by sending multiple requests"""
    print(f"\nTesting check-in links API (Airline: {airline_code}, Number of requests: {num_requests})...")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {"airlineCode": airline_code}
    
    async with aiohttp.ClientSession() as session:
        for i in range(num_requests):
            try:
                print(f"\nRequest {i+1}/{num_requests}:")
                async with session.get(CHECKIN_LINKS_ENDPOINT, params=params, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        links = result.get('data', [])
                        
                        print(f"  Status: Success")
                        print(f"  Found {len(links)} links")
                        
                        # Only print details of the first link
                        if links:
                            link = links[0]
                            print(f"  Link: {link.get('href')}")
                    else:
                        error_text = await response.text()
                        print(f"  Status: Failed (Code: {response.status})")
                        print(f"  Error: {error_text}")
            except Exception as e:
                print(f"  Status: Error")
                print(f"  Exception: {str(e)}")
            
            # Add small delay to avoid too rapid requests
            await asyncio.sleep(0.5)

async def main():
    """Main function"""
    # Check environment variables
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Amadeus API credentials not found, please ensure .env file contains AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET")
        return
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        print("Error: Unable to get access token, please check if API credentials are correct")
        return
    
    # Test check-in links API
    await test_checkin_links(access_token, airline_code="BA", num_requests=20)

if __name__ == "__main__":
    asyncio.run(main()) 