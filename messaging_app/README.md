# Messaging App with Django REST Framework

A RESTful API for user messaging built with Django and Django REST Framework (DRF).

## Features

- User authentication and authorization
- Conversation management between users
- Message sending within conversations
- RESTful API endpoints for all operations

## Technologies

- Python 3.x
- Django 4.x
- Django REST Framework
- SQLite (default, can be configured for other databases)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/messaging_app.git
   cd messaging_app
Create and activate a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Apply migrations:

bash
python manage.py migrate
Create a superuser:

bash
python manage.py createsuperuser
Run the development server:

bash
python manage.py runserver
API Endpoints
GET /api/conversations/ - List all conversations for authenticated user

POST /api/conversations/ - Create new conversation

GET /api/conversations/{id}/ - Retrieve specific conversation

GET /api/messages/ - List all messages in conversations user participates in

POST /api/messages/ - Send new message

Authentication
The API uses Django's session authentication by default. For production, consider implementing:

Token Authentication

JWT Authentication

Testing
Run the Django test suite:

bash
python manage.py test
License
MIT License