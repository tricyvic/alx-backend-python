from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Conversation, Message
import json

User = get_user_model()


class AuthenticationTestCase(TestCase):
    """
    Test case for authentication functionality.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
    def test_user_registration(self):
        """
        Test user registration endpoint.
        """
        response = self.client.post(
            reverse('register'),
            self.user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Check user was created
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        
    def test_user_login(self):
        """
        Test user login endpoint.
        """
        # Create user first
        user = User.objects.create_user(**self.user_data)
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(
            reverse('login_custom'),
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_jwt_token_authentication(self):
        """
        Test JWT token authentication.
        """
        # Create user and get token
        user = User.objects.create_user(**self.user_data)
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(
            reverse('token_obtain_pair'),
            login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        
        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(reverse('user_profile'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])


class PermissionsTestCase(TestCase):
    """
    Test case for permissions functionality.
    """
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123',
            first_name='User',
            last_name='One'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123',
            first_name='User',
            last_name='Two'
        )
        
        # Create a conversation with user1
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.user1)
        
    def test_conversation_access_permissions(self):
        """
        Test that users can only access conversations they participate in.
        """
        # Login as user1
        self.client.force_authenticate(user=self.user1)
        
        # User1 should see the conversation
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Login as user2
        self.client.force_authenticate(user=self.user2)
        
        # User2 should not see the conversation
        response = self.client.get('/api/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
    def test_message_creation_permissions(self):
        """
        Test that users can only create messages in conversations they participate in.
        """
        # Create a message as user1 (participant)
        self.client.force_authenticate(user=self.user1)
        
        message_data = {
            'conversation': self.conversation.conversation_id,
            'message_body': 'Hello from user1'
        }
        
        response = self.client.post('/api/messages/', message_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to create message as user2 (non-participant)
        self.client.force_authenticate(user=self.user2)
        
        message_data = {
            'conversation': self.conversation.conversation_id,
            'message_body': 'Hello from user2'
        }
        
        response = self.client.post('/api/messages/', message_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_message_modification_permissions(self):
        """
        Test that users can only modify their own messages.
        """
        # Create a message as user1
        message = Message.objects.create(
            sender=self.user1,
            conversation=self.conversation,
            message_body='Original message'
        )
        
        # Add user2 to conversation
        self.conversation.participants.add(self.user2)
        
        # User1 should be able to modify their message
        self.client.force_authenticate(user=self.user1)
        
        update_data = {'message_body': 'Updated message'}
        response = self.client.patch(
            f'/api/messages/{message.message_id}/',
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User2 should not be able to modify user1's message
        self.client.force_authenticate(user=self.user2)
        
        update_data = {'message_body': 'Trying to update'}
        response = self.client.patch(
            f'/api/messages/{message.message_id}/',
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)