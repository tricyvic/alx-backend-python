from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingTests(TestCase):
    def test_notification_created_on_message(self):
        sender = User.objects.create_user(username='sender', password='test')
        receiver = User.objects.create_user(username='receiver', password='test')
        message = Message.objects.create(sender=sender, receiver=receiver, content="Hello!")

        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, receiver)
        self.assertEqual(notification.message, message)
