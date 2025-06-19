# Test Documentation for AI Travel Assistant

This document provides comprehensive documentation for all test files in the `src/test/` directory.

## Overview

The test suite consists of 7 test files that validate the functionality of the AI Travel Assistant's integration with the Amadeus API. The tests cover various aspects including basic API functionality, asynchronous operations, service layer validation, and environment configuration.

## Test Files

### 1. test_amadeus_api.py
**Purpose**: Basic Amadeus API functionality test using the official SDK

**Key Features**:
- Tests airport search functionality
- Tests flight search functionality
- Uses the official Amadeus Python SDK
- Validates API credentials from environment variables
- Provides formatted output for debugging

**Test Cases**:
- Airport search with keyword "LON" (London airports)
- Flight search from London to Paris
- Error handling for invalid credentials
- Response data validation and formatting

**Location**: `src/test/test_amadeus_api.py:1`

### 2. test_amadeus_async.py
**Purpose**: Asynchronous testing of Amadeus API operations

**Key Features**:
- Implements async/await patterns for API calls
- Global client initialization
- Modular async functions for different API endpoints
- Chained testing workflow

**Test Cases**:
- Async client initialization
- Async airport search (Beijing - "BEI")
- Async flight search (using results from airport search)
- Error handling in async context

**Location**: `src/test/test_amadeus_async.py:1`

### 3. test_amadeus_checkin.py
**Purpose**: Focused testing of Amadeus check-in links API

**Key Features**:
- Direct HTTP calls using aiohttp
- Batch testing capability (20 requests)
- OAuth2 token management
- Rate limiting with delays

**Test Cases**:
- OAuth2 authentication flow
- Check-in links retrieval for British Airways
- Batch API testing for performance validation
- Error handling and status reporting

**Location**: `src/test/test_amadeus_checkin.py:1`

### 4. test_amadeus_direct.py
**Purpose**: Direct API testing without SDK dependencies

**Key Features**:
- Pure HTTP API calls using aiohttp
- Comprehensive endpoint coverage
- Batch testing capabilities
- Detailed response parsing

**Test Cases**:
- Authentication token acquisition
- Airport search (Beijing - "PEK")
- Flight search (Beijing to Shanghai)
- Check-in links retrieval
- Batch testing of check-in links API

**Location**: `src/test/test_amadeus_direct.py:1`

### 5. test_amadeus_service.py
**Purpose**: Service layer validation for the application's Amadeus service

**Key Features**:
- Tests the custom AmadeusService implementation
- Validates service methods and error handling
- Integration testing with logging
- Comprehensive functionality coverage

**Test Cases**:
- Service initialization and token management
- Airport search through service layer
- Flight search through service layer
- Check-in links through service layer
- Error handling and logging validation

**Location**: `src/test/test_amadeus_service.py:1`

### 6. test_api_endpoints.py
**Purpose**: Duplicate of test_amadeus_direct.py for comprehensive API testing

**Key Features**:
- Identical functionality to test_amadeus_direct.py
- Provides redundant testing for critical API endpoints
- Comprehensive endpoint validation

**Test Cases**:
- Same as test_amadeus_direct.py
- Serves as backup testing implementation

**Location**: `src/test/test_api_endpoints.py:1`

### 7. test_env_vars.py
**Purpose**: Environment variables validation and configuration testing

**Key Features**:
- Validates .env file loading
- Tests environment variable accessibility
- Masks sensitive information in output
- Comprehensive configuration validation

**Test Cases**:
- .env file discovery and reading
- Environment variable loading validation
- Sensitive data masking
- Configuration completeness check

**Location**: `src/test/test_env_vars.py:1`

## Common Dependencies

All test files share the following dependencies:
- `python-dotenv`: For environment variable loading
- `aiohttp`: For HTTP client operations (async tests)
- `requests`: For HTTP client operations (sync tests)
- `amadeus`: Official Amadeus SDK (where applicable)

## Environment Variables Required

The following environment variables must be configured:
- `AMADEUS_CLIENT_ID`: Amadeus API client identifier
- `AMADEUS_CLIENT_SECRET`: Amadeus API client secret
- `AMADEUS_HOST`: API host URL (optional, defaults to test environment)
- `OPENAI_API_KEY`: OpenAI API key (for AI features)

## Running Tests

Each test file is executable independently:
```bash
python src/test/test_amadeus_api.py
python src/test/test_amadeus_async.py
python src/test/test_amadeus_checkin.py
python src/test/test_amadeus_direct.py
python src/test/test_amadeus_service.py
python src/test/test_api_endpoints.py
python src/test/test_env_vars.py
```

## Test Coverage

The test suite covers:
- **API Authentication**: OAuth2 token management
- **Airport Search**: Location-based airport discovery
- **Flight Search**: Route and schedule queries
- **Check-in Links**: Airline-specific check-in URL retrieval
- **Service Layer**: Application service validation
- **Configuration**: Environment setup verification
- **Error Handling**: Comprehensive error scenarios
- **Performance**: Batch testing and rate limiting

## Notes

- All tests use the Amadeus test environment
- Sensitive data is masked in output logs
- Tests include comprehensive error handling
- Both synchronous and asynchronous patterns are tested
- Service layer abstraction is validated separately from direct API calls