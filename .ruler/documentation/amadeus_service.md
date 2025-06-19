# AmadeusService Documentation

## Overview

The `AmadeusService` class provides a comprehensive interface for interacting with the Amadeus API, focusing on travel-related operations including airport search, flight search, and airline check-in links retrieval. This service implements asynchronous operations using `aiohttp` for optimal performance.

**Location**: `src/services/amadeus_service.py:24`

## Class: AmadeusService

### Description
A service class that handles all Amadeus API interactions with automatic token management, error handling, and logging.

### Constructor

```python
def __init__(self):
```

**Purpose**: Initializes the Amadeus API service with configuration from environment variables.

**Functionality**:
- Loads API credentials from configuration
- Initializes token management variables
- Sets up logging for service operations

**Location**: `src/services/amadeus_service.py:29`

## Methods

### 1. _ensure_token()

```python
async def _ensure_token(self) -> Optional[str]:
```

**Purpose**: Ensures a valid access token is available, refreshing if expired.

**Returns**: 
- `Optional[str]`: Valid access token or None if authentication fails

**Features**:
- Automatic token refresh 60 seconds before expiration
- OAuth2 client credentials flow implementation
- Comprehensive error handling and logging
- Thread-safe token management

**Location**: `src/services/amadeus_service.py:39`

### 2. search_airports()

```python
async def search_airports(self, keyword: str, subtype: str = "AIRPORT") -> List[Dict[str, Any]]:
```

**Purpose**: Searches for airports using keyword matching.

**Parameters**:
- `keyword` (str): Search term (e.g., "LON" for London airports)
- `subtype` (str, optional): Location type filter, defaults to "AIRPORT"

**Returns**: 
- `List[Dict[str, Any]]`: List of airport data dictionaries

**Response Format**:
```json
[
  {
    "type": "location",
    "subType": "AIRPORT",
    "name": "London Heathrow Airport",
    "iataCode": "LHR",
    "address": {
      "cityName": "London",
      "countryName": "United Kingdom"
    }
  }
]
```

**Location**: `src/services/amadeus_service.py:80`

### 3. search_flights()

```python
async def search_flights(self, origin: str, destination: str, departure_date: str, 
                        adults: int = 1, max_results: int = 3) -> Dict[str, Any]:
```

**Purpose**: Searches for flight offers between two locations.

**Parameters**:
- `origin` (str): Origin airport code (e.g., "MAD")
- `destination` (str): Destination airport code (e.g., "BCN")
- `departure_date` (str): Departure date in "YYYY-MM-DD" format
- `adults` (int, optional): Number of adult passengers, defaults to 1
- `max_results` (int, optional): Maximum results to return, defaults to 3

**Returns**: 
- `Dict[str, Any]`: Flight search results with data and dictionaries

**Response Format**:
```json
{
  "data": [
    {
      "type": "flight-offer",
      "id": "1",
      "price": {
        "currency": "EUR",
        "total": "120.50"
      },
      "itineraries": [
        {
          "duration": "PT2H30M",
          "segments": [
            {
              "departure": {
                "iataCode": "MAD",
                "at": "2025-07-01T08:00:00"
              },
              "arrival": {
                "iataCode": "BCN",
                "at": "2025-07-01T10:30:00"
              },
              "carrierCode": "IB",
              "number": "1234"
            }
          ]
        }
      ]
    }
  ],
  "dictionaries": {
    "carriers": {
      "IB": "Iberia"
    }
  }
}
```

**Error Response**:
```json
{
  "error": "Error message",
  "data": []
}
```

**Location**: `src/services/amadeus_service.py:121`

### 4. get_flight_checkin_links()

```python
async def get_flight_checkin_links(self, airline_code: str) -> List[Dict[str, Any]]:
```

**Purpose**: Retrieves check-in links for a specific airline.

**Parameters**:
- `airline_code` (str): IATA airline code (e.g., "BA" for British Airways)

**Returns**: 
- `List[Dict[str, Any]]`: List of check-in link information

**Response Format**:
```json
[
  {
    "type": "checkin-link",
    "airlineCode": "BA",
    "href": "https://checkin.britishairways.com/",
    "type": "WEB_CHECKIN"
  }
]
```

**Location**: `src/services/amadeus_service.py:174`

## Configuration

### Environment Variables

The service requires the following environment variables:

- `AMADEUS_CLIENT_ID`: Amadeus API client identifier
- `AMADEUS_CLIENT_SECRET`: Amadeus API client secret
- `AMADEUS_HOST`: Environment setting ("test" or "production")

### API Endpoints

The service automatically configures endpoints based on the environment:

**Test Environment** (default):
- Authentication: `https://test.api.amadeus.com/v1/security/oauth2/token`
- Airport Search: `https://test.api.amadeus.com/v1/reference-data/locations`
- Flight Search: `https://test.api.amadeus.com/v2/shopping/flight-offers`
- Check-in Links: `https://test.api.amadeus.com/v2/reference-data/urls/checkin-links`

**Production Environment** (when `AMADEUS_HOST="production"`):
- All endpoints use `api.amadeus.com` instead of `test.api.amadeus.com`

**Location**: `src/services/amadeus_service.py:12-22`

## Service Instance

A singleton instance is created and exported:

```python
amadeus_service = AmadeusService()
```

**Usage**:
```python
from src.services.amadeus_service import amadeus_service

# Search airports
airports = await amadeus_service.search_airports("LON")

# Search flights
flights = await amadeus_service.search_flights("LHR", "CDG", "2025-07-01")

# Get check-in links
links = await amadeus_service.get_flight_checkin_links("BA")
```

**Location**: `src/services/amadeus_service.py:212`

## Error Handling

The service implements comprehensive error handling:

1. **Authentication Errors**: Automatic retry with detailed logging
2. **HTTP Errors**: Status code validation with error message extraction
3. **Network Errors**: Exception catching with graceful degradation
4. **Token Expiration**: Automatic refresh before expiration

## Logging

All operations are logged using the application's logging system:

- **Info Level**: Successful operations and API calls
- **Error Level**: Failed operations with detailed error messages
- **Debug Level**: Token management and internal state changes

## Dependencies

- `aiohttp`: Asynchronous HTTP client
- `asyncio`: Asynchronous programming support
- `typing`: Type hints for better code documentation
- `src.config.settings`: Application configuration
- `src.utils.logger`: Logging utilities

## Usage Examples

### Basic Airport Search
```python
airports = await amadeus_service.search_airports("NYC")
for airport in airports:
    print(f"{airport['name']} ({airport['iataCode']})")
```

### Flight Search with Error Handling
```python
result = await amadeus_service.search_flights("JFK", "LAX", "2025-08-15")
if result.get("error"):
    print(f"Flight search failed: {result['error']}")
else:
    flights = result["data"]
    print(f"Found {len(flights)} flights")
```

### Airline Check-in Links
```python
links = await amadeus_service.get_flight_checkin_links("AA")
for link in links:
    print(f"Check-in: {link['href']}")
```

## Performance Considerations

- **Token Caching**: Access tokens are cached and reused until near expiration
- **Connection Pooling**: Uses aiohttp's connection pooling for efficiency
- **Asynchronous Operations**: All API calls are non-blocking
- **Error Recovery**: Graceful handling of temporary failures

## Security Features

- **Credential Protection**: API secrets are loaded from environment variables
- **Token Management**: Secure token storage with automatic refresh
- **Request Validation**: Parameter validation before API calls
- **Error Sanitization**: Sensitive information excluded from logs