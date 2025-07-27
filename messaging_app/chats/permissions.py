from rest_framework import permissions
from rest_framework.permissions import BasePermission
from .models import Conversation, Message


class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    message = "You must be a participant of this conversation to perform this action."

    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if a user is a participant of the conversation
        """
        # For Conversation objects
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        
        # For Message objects
        if isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
        
        return False


class IsMessageSenderOrParticipant(BasePermission):
    """
    Custom permission for message-specific actions.
    - Anyone who is a participant can view messages
    - Only the sender can delete their own messages
    - Only participants can create/update messages
    """
    message = "You don't have permission to perform this action on this message."

    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check permissions based on the action
        """
        if not isinstance(obj, Message):
            return False

        # Check if a user is a participant of the conversation
        is_participant = request.user in obj.conversation.participants.all()
        
        if request.method in permissions.SAFE_METHODS:
            # For read operations (GET), user must be a participant
            return is_participant
        
        elif request.method == 'DELETE':
            # For delete operations, user must be the sender
            return obj.sender == request.user
        
        elif request.method in ['PUT', 'PATCH']:
            # For update operations, user must be the sender
            return obj.sender == request.user
        
        elif request.method == 'POST':
            # For create operations, user must be a participant
            # This will be handled in the view's perform_create method
            return is_participant
        
        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner of the object
        return obj.sender == request.user


class IsConversationParticipant(BasePermission):
    """
    Permission specifically for conversation access
    """
    message = "You must be a participant of this conversation."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        return False