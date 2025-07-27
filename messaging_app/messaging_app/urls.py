from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.routers import DefaultRouter
from chats.views import ConversationViewSet, MessageViewSet, UserRegistrationView, UserProfileView

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user_profile'),
]

# Sample payload for user registration
sample_user_payload = {
    "username": "testuser1",
    "email": "testuser1@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User1"
}