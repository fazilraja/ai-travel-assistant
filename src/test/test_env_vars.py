#!/usr/bin/env python3
"""
Environment Variables Test Script

This script tests if environment variables are loaded correctly
"""

import os
from dotenv import load_dotenv, find_dotenv

def main():
    """Test environment variables loading"""
    print("Looking for .env file...")
    dotenv_path = find_dotenv()
    if dotenv_path:
        print(f"Found .env file: {dotenv_path}")
    else:
        print("Could not find .env file")
        return
    
    print("\nTesting direct reading of .env file contents...")
    try:
        with open(dotenv_path, 'r') as f:
            content = f.read()
            print("File contents:")
            for line in content.split('\n'):
                # Hide sensitive information, only show partial content
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if 'SECRET' in key or 'KEY' in key:
                        masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '*' * len(value)
                        print(f"  {key}={masked_value}")
                    else:
                        print(f"  {key}={value}")
                else:
                    print(f"  {line}")
    except Exception as e:
        print(f"Failed to read file: {e}")
    
    print("\nLoading environment variables...")
    load_dotenv()
    
    print("\nTesting environment variables reading...")
    vars_to_check = [
        "AMADEUS_CLIENT_ID",
        "AMADEUS_CLIENT_SECRET", 
        "AMADEUS_HOST",
        "OPENAI_API_KEY"
    ]
    
    for var in vars_to_check:
        value = os.getenv(var)
        if value:
            # Hide sensitive information
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '*' * len(value)
                print(f"  {var}: {masked_value}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: Not set")

if __name__ == "__main__":
    main()