"""Публичные схемы API."""

from .menu import ContentFileResponse, MenuContentResponse, MenuItemResponse
from .ratings import RatingRequest, RatingResponse
from .search import SearchListResponse
from .user_activity import UserActivityRequest, UserActivityResponse
from .user_question import UserQuestionCreate, UserQuestionResponse


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
