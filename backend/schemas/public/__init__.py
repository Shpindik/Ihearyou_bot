"""Публичные схемы API."""

from .menu import ContentFileResponse, MenuContentResponse, MenuItemListResponse, MenuItemResponse
from .ratings import RatingRequest, RatingResponse
from .search import SearchListResponse
from .user_activity import UserActivityRequest, UserActivityResponse
from .user_question import UserQuestionCreate, UserQuestionResponse


__all__ = [
    # Menu
    "MenuItemResponse",
    "MenuItemListResponse",
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
