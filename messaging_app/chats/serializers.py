from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['id', 'sender', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participant_ids', 'created_at']
        read_only_fields = ['id', 'participants', 'created_at']

    def create(self, validated_data):
        participant_users = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create()
        conversation.participants.set(participant_users)
        return conversation
