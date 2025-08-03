# chats/views.py

from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404
from messaging.models import Message
from django.contrib.auth.models import User

@cache_page(60)  # ⏱️ cache this view for 60 seconds
def conversation_messages(request, username):
    user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        sender=request.user, receiver=user
    ) | Message.objects.filter(
        sender=user, receiver=request.user
    )
    messages = messages.order_by('timestamp')
    
    return render(request, 'chats/conversation.html', {
        'messages': messages,
        'conversation_with': user,
    })
