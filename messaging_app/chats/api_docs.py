"""
API Filtering and Pagination Documentation

=== MESSAGES API ===

GET /api/messages/
Supports the following query parameters:

Pagination:
- page: Page number (default: 1)
- page_size: Number of items per page (default: 20, max: 100)

Filtering:
- conversation: Filter by conversation ID
  Example: /api/messages/?conversation=1

- sender_username: Filter by sender username (partial match)
  Example: /api/messages/?sender_username=john

- sender: Filter by sender ID
  Example: /api/messages/?sender=1

- content: Search in message content (partial match)
  Example: /api/messages/?content=hello

- date_from: Messages sent after this datetime
  Example: /api/messages/?date_from=2023-01-01T00:00:00Z

- date_to: Messages sent before this datetime
  Example: /api/messages/?date_to=2023-12-31T23:59:59Z

- sent_date: Messages sent on specific date
  Example: /api/messages/?sent_date=2023-07-23

- last_days: Messages from last N days
  Example: /api/messages/?last_days=7

Search:
- search: Search in message content
  Example: /api/messages/?search=hello

Ordering:
- ordering: Order by field (prefix with '-' for descending)
  Example: /api/messages/?ordering=-sent_at

=== CONVERSATIONS API ===

GET /api/conversations/
Supports the following query parameters:

Pagination:
- page: Page number (default: 1)
- page_size: Number of items per page (default: 10, max: 50)

Filtering:
- name: Filter by conversation name (partial match)
  Example: /api/conversations/?name=team

- participant_username: Conversations with specific participant
  Example: /api/conversations/?participant_username=john

- participant_id: Conversations with specific participant ID
  Example: /api/conversations/?participant_id=1

- created_from: Conversations created after datetime
  Example: /api/conversations/?created_from=2023-01-01T00:00:00Z

- created_to: Conversations created before datetime
  Example: /api/conversations/?created_to=2023-12-31T23:59:59Z

- min_participants: Conversations with at least N participants
  Example: /api/conversations/?min_participants=3

- max_participants: Conversations with at most N participants
  Example: /api/conversations/?max_participants=5

Search:
- search: Search in conversation name
  Example: /api/conversations/?search=project

Ordering:
- ordering: Order by field (prefix with '-' for descending)
  Example: /api/conversations/?ordering=-created_at

=== COMBINED EXAMPLES ===

# Get messages from conversation 1, sent in last 7 days, paginated
/api/messages/?conversation=1&last_days=7&page=1&page_size=10

# Get conversations with user 'john', ordered by creation date
/api/conversations/?participant_username=john&ordering=-created_at

# Search messages containing 'meeting' from last 30 days
/api/messages/?search=meeting&last_days=30&page_size=50
"""