import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    email = models.EmailField(
        unique=True,
        verbose_name='email address',
        help_text="User's email address"
    )

    first_name = models.CharField(
        max_length=150,
        blank=False,  # Making required (default is blank=True)
        verbose_name='first name'
    )
    
    last_name = models.CharField(
        max_length=150,
        blank=False,  # Making required (default is blank=True)
        verbose_name='last name'
    )

    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey('Conversation', on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(  # Changed from 'body' to 'message_body'
        verbose_name='message content',
        help_text="The actual content of the message",
        blank=False,  # Equivalent to NOT NULL
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message {self.id} from {self.sender}"