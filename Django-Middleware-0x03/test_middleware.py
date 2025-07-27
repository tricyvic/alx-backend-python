#!/usr/bin/env python
"""
Test script to demonstrate the RestrictAccessByTimeMiddleware functionality.
This script shows what the middleware does during restricted hours.
"""

from datetime import datetime, time

def test_time_restriction():
    """
    Simulate the time restriction logic used in the middleware
    """
    # Current server time (for demo purposes, we'll simulate different times)
    test_times = [
        datetime.strptime("05:30", "%H:%M").time(),  # Before allowed hours
        datetime.strptime("06:00", "%H:%M").time(),  # Start of allowed hours
        datetime.strptime("12:00", "%H:%M").time(),  # During allowed hours
        datetime.strptime("20:59", "%H:%M").time(),  # End of allowed hours
        datetime.strptime("21:00", "%H:%M").time(),  # After allowed hours
        datetime.strptime("23:30", "%H:%M").time(),  # Late night
    ]
    
    # Middleware settings
    start_hour = 6  # 6 AM
    end_hour = 21   # 9 PM
    
    print("RestrictAccessByTimeMiddleware Test Results:")
    print("=" * 50)
    print(f"Allowed hours: {start_hour}:00 AM to {end_hour}:00 (9:00 PM)")
    print()
    
    for test_time in test_times:
        current_hour = test_time.hour
        is_allowed = start_hour <= current_hour < end_hour
        status = "✅ ALLOWED" if is_allowed else "❌ FORBIDDEN (403)"
        
        print(f"Time: {test_time.strftime('%H:%M')} - {status}")
    
    print()
    print("Current server time:", datetime.now().strftime('%H:%M:%S'))
    current_hour = datetime.now().hour
    is_currently_allowed = start_hour <= current_hour < end_hour
    current_status = "✅ ALLOWED" if is_currently_allowed else "❌ FORBIDDEN (403)"
    print(f"Current access status: {current_status}")

if __name__ == "__main__":
    test_time_restriction()
