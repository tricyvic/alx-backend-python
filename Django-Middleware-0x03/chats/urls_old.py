from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Initialize the DefaultRouter
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]

# Register your ViewSets with the router
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Create nested router for messages within conversations
conversations_router = NestedDefaultRouter(
    router, r"conversations", lookup="conversation"
)

urlpatterns = [
    # Include the router-generated URLs
    path('', include(router.urls)),
    
    # You can add additional non-ViewSet URLs here if needed
    # path('custom-endpoint/', custom_view, name='custom-view'),
]
