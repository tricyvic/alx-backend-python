from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Conversation, Message

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password fields didn't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'full_name']
        read_only_fields = ['id', 'username']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'conversation', 'message_body', 'sent_at']
    
    def validate_message_body(self, value):
        """Example of field-level validation"""
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Message cannot be empty")
        if 'badword' in value.lower():
            raise serializers.ValidationError("Message contains inappropriate content")
        return value
    
    def validate(self, attrs):
        """Example of object-level validation"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if request.user not in attrs['conversation'].participants.all():
                raise serializers.ValidationError("Sender must be a conversation participant")
        return attrs

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'messages']