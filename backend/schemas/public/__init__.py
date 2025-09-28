"""Публичные схемы API."""

from .menu import (
    MenuItemResponse,
    MenuContentResponse,
    ContentFileResponse,
)
from .ratings import (
    RatingRequest,
    RatingResponse,
)
from .search import (
    SearchListResponse,
)
from .user_activities import (
    UserActivityRequest,
    UserActivityResponse,
)
from .user_questions import (
    UserQuestionCreate,
    UserQuestionResponse,
)

__all__ = [
    # Menu
    "MenuItemResponse",
    "MenuContentResponse",
    "ContentFileResponse",
    # Ratings
    "RatingRequest",
    "RatingResponse",
    # Search
    "SearchListResponse",
    # User Activities
    "UserActivityRequest",
    "UserActivityResponse",
    # User Questions
    "UserQuestionCreate",
    "UserQuestionResponse",
]
