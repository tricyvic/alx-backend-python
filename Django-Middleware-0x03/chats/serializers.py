from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'message_body', 'sent_at']
    
    def validate_message_body(self, value):
        """Example of field-level validation"""
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Message cannot be empty")
        if 'badword' in value.lower():
            raise serializers.ValidationError("Message contains inappropriate content")
        return value
    
    def validate(self, attrs):
        """Example of object-level validation"""
        if attrs['sender'] not in attrs['conversation'].participants.all():
            raise serializers.ValidationError("Sender must be a conversation participant")
        return attrs


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'messages']
