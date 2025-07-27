# messaging_app/chats/admin.py

"""
Admin registration for chats app models: User, Conversation, Message
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Conversation, Message, User


# Custom User Admin configuration
class CustomUserAdmin(UserAdmin):
    """Custom User model display in admin"""

    # Fields to display in the admin list view
    list_display = ("email", "first_name", "last_name", "role", "is_active", "is_staff")

    # Fields available for filtering
    list_filter = ("role", "is_active", "is_staff")

    # Fieldsets for the edit view
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone_number")}),
        (
            "Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields when adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Default ordering
    ordering = ("email",)
    search_fields = ("email", "first_name", "last_name")


# Register Conversation with inline for messages
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0  # No extra blank forms
    fields = ("sender", "message_body", "sent_at")
    readonly_fields = ("sent_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin view for Conversation model"""

    list_display = ("id", "created_at", "participants_list")
    filter_horizontal = ("participants",)  # Better widget for many-to-many
    inlines = [MessageInline]

    @admin.display(description="Participants")
    def participants_list(self, obj):
        return ", ".join([user.email for user in obj.participants.all()])


# Register Message model
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin view for Message model"""

    list_display = (
        "id",
        "sender",
        "conversation",
        "sent_at",
        "short_message_body",
    )
    list_filter = ("sender", "conversation")
    search_fields = ("message_body", "sender__email")
    date_hierarchy = "sent_at"

    @admin.display(description="Message")
    def short_message_body(self, obj):
        return (
            obj.message_body[:50] + "..."
            if len(obj.message_body) > 50
            else obj.message_body
        )


# Register the custom User model
admin.site.register(User, CustomUserAdmin)