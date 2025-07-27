from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import QuerySet
from typing import Any
from rest_framework.decorators import action

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer, UserRegistrationSerializer
from .permissions import IsParticipantOfConversation, IsMessageSenderOrParticipant, IsConversationParticipant
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination, ConversationPagination
from .auth import TokenService, AuthenticationHelper

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile management
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return the current authenticated user"""
        return self.request.user


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    pagination_class = ConversationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Only return conversations the authenticated user is part of"""
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """Automatically add the current user as a participant when creating a conversation"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific conversation with proper permission checking"""
        try:
            instance = self.get_object()
            # Check if user is a participant
            if request.user not in instance.participants.all():
                return Response(
                    {"error": "You don't have permission to access this conversation"},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "Conversation not found or access denied"},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific conversation"""
        try:
            conversation = self.get_object()
            conversation_id = conversation.id
            
            # Check if user is a participant
            if request.user not in conversation.participants.all():
                return Response(
                    {"error": "You don't have permission to access messages in this conversation"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            messages = Message.objects.filter(conversation_id=conversation_id).order_by('-sent_at')
            serializer = MessageSerializer(messages, many=True)
            return Response({
                "conversation_id": conversation_id,
                "messages": serializer.data
            })
        except Exception as e:
            return Response(
                {"error": "Failed to retrieve messages"},
                status=status.HTTP_403_FORBIDDEN
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsMessageSenderOrParticipant]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['content']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """Only return messages from conversations the user is part of"""
        if not self.request.user.is_authenticated:
            return Message.objects.none()
        
        queryset = Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').prefetch_related('conversation__participants')
        
        # Filter by conversation_id if provided
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            try:
                # Verify user has access to this conversation
                conversation = Conversation.objects.get(id=conversation_id)
                if self.request.user not in conversation.participants.all():
                    return Message.objects.none()
                queryset = queryset.filter(conversation_id=conversation_id)
            except Conversation.DoesNotExist:
                return Message.objects.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Ensure the user is part of the conversation before creating a message"""
        conversation = serializer.validated_data['conversation']
        conversation_id = conversation.id
        
        # Check if user is part of the conversation
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You're not part of this conversation")
        
        # Save with the current user as sender
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a new message with enhanced error handling"""
        try:
            # Validate conversation_id if provided
            conversation_id = request.data.get('conversation')
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    if request.user not in conversation.participants.all():
                        return Response(
                            {
                                "error": "You don't have permission to send messages to this conversation",
                                "conversation_id": conversation_id
                            },
                            status=status.HTTP_403_FORBIDDEN
                        )
                except Conversation.DoesNotExist:
                    return Response(
                        {
                            "error": "Conversation not found",
                            "conversation_id": conversation_id
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            return Response(
                {
                    "message": "Message sent successfully",
                    "conversation_id": serializer.instance.conversation.id,
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except PermissionDenied as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {"error": "Failed to send message"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Delete a message with proper error handling"""
        try:
            instance = self.get_object()
            conversation_id = instance.conversation.id
            
            # Check if user is the sender
            if instance.sender != request.user:
                return Response(
                    {
                        "error": "You can only delete your own messages",
                        "conversation_id": conversation_id
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            self.perform_destroy(instance)
            return Response(
                {
                    "message": "Message deleted successfully",
                    "conversation_id": conversation_id
                },
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": "Failed to delete message"},
                status=status.HTTP_403_FORBIDDEN
            )

    def update(self, request, *args, **kwargs):
        """Update a message with permission checking"""
        try:
            instance = self.get_object()
            conversation_id = instance.conversation.id
            
            # Check if user is the sender
            if instance.sender != request.user:
                return Response(
                    {
                        "error": "You can only edit your own messages",
                        "conversation_id": conversation_id
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(
                {
                    "message": "Message updated successfully",
                    "conversation_id": conversation_id,
                    "data": serializer.data
                }
            )
        except Exception as e:
            return Response(
                {"error": "Failed to update message"},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """Get messages filtered by conversation_id"""
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {"error": "conversation_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify conversation exists and user has access
            conversation = Conversation.objects.get(id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {
                        "error": "You don't have permission to access messages in this conversation",
                        "conversation_id": conversation_id
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get messages
            messages = Message.objects.filter(
                conversation_id=conversation_id
            ).order_by('-sent_at')
            
            # Apply pagination
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    "conversation_id": conversation_id,
                    "messages": serializer.data
                })
            
            serializer = self.get_serializer(messages, many=True)
            return Response({
                "conversation_id": conversation_id,
                "messages": serializer.data
            })
            
        except Conversation.DoesNotExist:
            return Response(
                {
                    "error": "Conversation not found",
                    "conversation_id": conversation_id
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {
                    "error": "Failed to retrieve messages",
                    "conversation_id": conversation_id
                },
                status=status.HTTP_403_FORBIDDEN
            )
