from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.page_size),
            ('results', data)
        ]))


class ConversationPagination(PageNumberPagination):
    """
    Custom pagination class for conversations
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.page_size),
            ('results', data)
        ]))


import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Message, Conversation

User = get_user_model()


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for messages with various filtering options
    """
    # Filter by conversation ID
    conversation = django_filters.NumberFilter(
        field_name='conversation__id',
        help_text="Filter messages by conversation ID"
    )
    
    # Filter by sender username
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text="Filter messages by sender username (case-insensitive partial match)"
    )
    
    # Filter by sender ID
    sender = django_filters.NumberFilter(
        field_name='sender__id',
        help_text="Filter messages by sender ID"
    )
    
    # Filter by content (search in message content)
    content = django_filters.CharFilter(
        field_name='content',
        lookup_expr='icontains',
        help_text="Search messages by content (case-insensitive partial match)"
    )
    
    # Date range filters
    date_from = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text="Filter messages sent after this datetime (YYYY-MM-DD HH:MM:SS)"
    )
    
    date_to = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text="Filter messages sent before this datetime (YYYY-MM-DD HH:MM:SS)"
    )
    
    # Date range as a single filter
    date_range = django_filters.DateFromToRangeFilter(
        field_name='sent_at',
        help_text="Filter messages within a date range"
    )
    
    # Filter by specific date
    sent_date = django_filters.DateFilter(
        field_name='sent_at__date',
        help_text="Filter messages sent on a specific date (YYYY-MM-DD)"
    )
    
    # Filter messages from last N days
    last_days = django_filters.NumberFilter(
        method='filter_last_days',
        help_text="Filter messages from last N days"
    )
    
    # Filter by read status (if you have this field)
    # is_read = django_filters.BooleanFilter(
    #     field_name='is_read',
    #     help_text="Filter by read status"
    # )

    class Meta:
        model = Message
        fields = {
            'sent_at': ['exact', 'gte', 'lte', 'year', 'month', 'day'],
            'conversation': ['exact'],
            'sender': ['exact'],
        }

    def filter_last_days(self, queryset, name, value):
        """
        Custom filter to get messages from last N days
        """
        if value:
            from django.utils import timezone
            from datetime import timedelta
            
            cutoff_date = timezone.now() - timedelta(days=value)
            return queryset.filter(sent_at__gte=cutoff_date)
        return queryset


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for conversations
    """
    # Filter by conversation name
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text="Filter conversations by name (case-insensitive partial match)"
    )
    
    # Filter conversations with specific user
    participant_username = django_filters.CharFilter(
        method='filter_by_participant_username',
        help_text="Filter conversations that include a specific participant (username)"
    )
    
    participant_id = django_filters.NumberFilter(
        method='filter_by_participant_id',
        help_text="Filter conversations that include a specific participant (user ID)"
    )
    
    # Filter by creation date
    created_from = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text="Filter conversations created after this datetime"
    )
    
    created_to = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text="Filter conversations created before this datetime"
    )
    
    # Filter by participant count
    min_participants = django_filters.NumberFilter(
        method='filter_min_participants',
        help_text="Filter conversations with at least N participants"
    )
    
    max_participants = django_filters.NumberFilter(
        method='filter_max_participants',
        help_text="Filter conversations with at most N participants"
    )

    class Meta:
        model = Conversation
        fields = {
            'created_at': ['exact', 'gte', 'lte', 'year', 'month', 'day'],
            'name': ['exact', 'icontains'],
        }

    def filter_by_participant_username(self, queryset, name, value):
        """
        Filter conversations that include a participant with the given username
        """
        if value:
            return queryset.filter(participants__username__icontains=value).distinct()
        return queryset

    def filter_by_participant_id(self, queryset, name, value):
        """
        Filter conversations that include a participant with the given user ID
        """
        if value:
            return queryset.filter(participants__id=value).distinct()
        return queryset

    def filter_min_participants(self, queryset, name, value):
        """
        Filter conversations with at least N participants
        """
        if value:
            from django.db.models import Count
            return queryset.annotate(
                participant_count=Count('participants')
            ).filter(participant_count__gte=value)
        return queryset

    def filter_max_participants(self, queryset, name, value):
        """
        Filter conversations with at most N participants
        """
        if value:
            from django.db.models import Count
            return queryset.annotate(
                participant_count=Count('participants')
            ).filter(participant_count__lte=value)
        return queryset