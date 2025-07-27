from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
# Removed unused import of TestCase from django.test
User = get_user_model()

class PermissionTestCase(APITestCase):
    def setUp(self):
        # Ensure APIClient is used for self.client
        from rest_framework.test import APIClient
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='user2@example.com',
            password='testpass123'
        )
    def test_authenticated_user_access(self):
        # Log in the user for authentication
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthenticated_access_denied(self):
        # Test without authentication
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_can_only_see_own_conversations(self):
        # Authenticate as user1
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.get('/api/conversations/')
        # Add your assertions here
        
    # No need for tearDown since APIClient is used and each test gets a fresh client instance