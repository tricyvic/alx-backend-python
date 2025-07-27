from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.conversations.all() # type: ignore

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    from typing import Any
    from django.db.models.query import QuerySet

    def get_queryset(self) -> 'QuerySet[Message]': # type: ignore
        # Start with messages where the user is a participant
        queryset = Message.objects.filter(conversation__participants=self.request.user)
        
        # Filter by query parameters
        conversation_id = self.request.GET.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
            
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from and date_to:
            queryset = queryset.filter(
                sent_at__range=[date_from, date_to]
            )
            
        return queryset.order_by('-sent_at')
    
    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            raise permissions.exceptions.PermissionDenied("You're not part of this conversation")
        serializer.save(sender=self.request.user)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, 
            status=status.HTTP_201_CREATED,  # Status code
            headers=headers
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Message deleted successfully"},
            status=status.HTTP_204_NO_CONTENT  # Status code
        )

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["sender__role"]
    ordering_fields = ["sent_at"]
    ordering = ["-sent_at"]
    search_fields = ["message_body", "sender__first_name", "sender__last_name"]
