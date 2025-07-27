"""
Django Middleware Configuration Summary
======================================

This project now has three custom middleware components working together:

1. OffensiveLanguageMiddleware (Rate Limiting)
2. RestrictAccessByTimeMiddleware (Time-based Access Control)  
3. RequestLoggingMiddleware (Request Logging)

MIDDLEWARE ORDER in settings.py:
------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", 
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "chats.middleware.OffensiveLanguageMiddleware",     # Rate limiting (5 req/min)
    "chats.middleware.RestrictAccessByTimeMiddleware",  # Time restriction (6AM-9PM)
    "chats.middleware.RequestLoggingMiddleware",        # Request logging
]

MIDDLEWARE FUNCTIONALITY:
------------------------

1. OffensiveLanguageMiddleware:
   - Limits POST requests to messaging endpoints
   - Maximum 5 messages per minute per IP address
   - Returns HTTP 429 "Too Many Requests" when limit exceeded
   - Tracks requests using IP address and timestamps
   - Automatic cleanup of old request data

2. RestrictAccessByTimeMiddleware:
   - Blocks access to messaging features outside business hours
   - Allowed hours: 6:00 AM to 9:00 PM
   - Returns HTTP 403 "Forbidden" during restricted hours
   - Only affects messaging paths (/api/v1/, /messages/, /conversations/)
   - Admin and other paths remain accessible

3. RequestLoggingMiddleware:
   - Logs all requests to logs/requests.log
   - Format: "TIMESTAMP - User: USERNAME - Path: REQUEST_PATH"
   - Shows "Anonymous" for unauthenticated users
   - Logs both successful and blocked requests

TESTING RESULTS:
---------------
✅ Rate limiting working: 429 error after 5 POST requests in 1 minute
✅ Time restriction working: 403 error outside allowed hours
✅ Request logging working: All requests logged to requests.log
✅ Middleware order correct: Rate limiting → Time restriction → Logging
✅ Non-messaging paths unaffected: Homepage and admin accessible

EXAMPLE ERROR RESPONSES:
-----------------------

Rate Limit Exceeded (429):
"You have exceeded the rate limit for sending messages.
Limit: 5 messages per minute
Please wait before sending another message."

Time Restriction (403):
"Access to the messaging app is restricted.
Please try again between 6:00 AM and 9:00 PM."

Log Entry Example:
"2025-07-24 18:41:16.218122 - User: Anonymous - Path: /api/v1/messages/"
"""

print(__doc__)
