#!/usr/bin/env python
"""
Test script to demonstrate the OffensiveLanguageMiddleware (Rate Limiting) functionality.
This script simulates multiple POST requests to test the rate limiting.
"""

import requests
import time
import json
from datetime import datetime

def test_rate_limiting():
    """
    Test the rate limiting middleware by making multiple POST requests
    """
    base_url = "http://127.0.0.1:8000"
    
    # Test endpoints that should be rate limited (POST requests to messaging)
    test_endpoints = [
        "/api/v1/messages/",
        "/api/v1/conversations/"
    ]
    
    print("Rate Limiting Middleware Test")
    print("=" * 50)
    print("Rate limit: 5 messages per minute")
    print("Testing POST requests to messaging endpoints...")
    print()
    
    for endpoint in test_endpoints:
        url = base_url + endpoint
        print(f"Testing endpoint: {endpoint}")
        print("-" * 30)
        
        # Make 7 POST requests quickly to test rate limiting
        for i in range(1, 8):
            try:
                # Make POST request with dummy data
                response = requests.post(
                    url, 
                    json={"test": f"message {i}"}, 
                    timeout=5,
                    headers={'Content-Type': 'application/json'}
                )
                
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                if response.status_code == 429:
                    print(f"Request {i} [{timestamp}]: ❌ RATE LIMITED (429) - {response.reason}")
                    # Print the rate limit message if available
                    if 'text/html' in response.headers.get('content-type', ''):
                        print(f"  Rate limit message received")
                    break
                elif response.status_code == 403:
                    print(f"Request {i} [{timestamp}]: ⚠️ Forbidden (403) - Might be time restriction")
                elif response.status_code in [200, 201]:
                    print(f"Request {i} [{timestamp}]: ✅ SUCCESS ({response.status_code})")
                elif response.status_code in [400, 404, 405]:
                    print(f"Request {i} [{timestamp}]: ⚠️ Expected error ({response.status_code}) - {response.reason}")
                else:
                    print(f"Request {i} [{timestamp}]: ❓ Unexpected ({response.status_code}) - {response.reason}")
                
                # Small delay between requests
                time.sleep(0.2)
                
            except requests.exceptions.ConnectionError:
                print(f"Request {i}: ❌ CONNECTION ERROR - Server might be down")
                break
            except requests.exceptions.Timeout:
                print(f"Request {i}: ❌ TIMEOUT - Request took too long")
                break
            except Exception as e:
                print(f"Request {i}: ❌ ERROR - {str(e)}")
                break
        
        print()
    
    print("Test completed!")
    print("\nNote: If you see 405 Method Not Allowed, that's expected")
    print("because we're testing POST to endpoints that might not exist yet.")
    print("The important thing is to see if rate limiting (429) occurs.")

if __name__ == "__main__":
    test_rate_limiting()
