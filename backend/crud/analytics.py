"""CRUD операции для аналитики системы."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import MenuItem, TelegramUser


class AnalyticsCRUD:
    """CRUD для аналитических запросов и статистики.

    - ORM для простых запросов (COUNT, базовые фильтры)
    - SQL для сложной аналитики (агрегации, FILTER, оконные функции)
    """

    def __init__(self):
        """Инициализация AnalyticsCRUD."""

    async def get_users_statistics(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Получить статистику пользователей.

        Args:
            db: Сессия базы данных
            start_date: Начальная дата фильтрации
            end_date: Конечная дата фильтрации

        Returns:
            Словарь со статистикой пользователей

        """
        total_result = await db.execute(select(func.count(TelegramUser.id)))
        total = total_result.scalar()

        today_start = datetime.combine(date.today(), datetime.min.time())
        today_result = await db.execute(
            select(func.count(TelegramUser.id)).where(TelegramUser.last_activity >= today_start)
        )
        active_today = today_result.scalar()

        from datetime import timedelta

        week_ago = datetime.now() - timedelta(days=7)
        week_result = await db.execute(
            select(func.count(TelegramUser.id)).where(TelegramUser.last_activity >= week_ago)
        )
        active_week = week_result.scalar()

        month_ago = datetime.now() - timedelta(days=30)
        month_result = await db.execute(
            select(func.count(TelegramUser.id)).where(TelegramUser.last_activity >= month_ago)
        )
        active_month = month_result.scalar()

        return {
            "total": total or 0,
            "active_today": active_today or 0,
            "active_week": active_week or 0,
            "active_month": active_month or 0,
        }

    async def get_content_statistics(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Получить статистику контента.

        Args:
            db: Сессия базы данных
            start_date: Начальная дата фильтрации
            end_date: Конечная дата фильтрации

        Returns:
            Словарь со статистикой контента

        """
        total_items_result = await db.execute(select(func.count(MenuItem.id)).where(MenuItem.is_active))
        total_menu_items = total_items_result.scalar()

        most_viewed_query = text("""
            SELECT id, title, view_count, download_count, 
                   COALESCE(average_rating, 0) as average_rating
            FROM menu_items 
            WHERE is_active = true 
            ORDER BY view_count DESC 
            LIMIT 10
        """)
        most_viewed_result = await db.execute(most_viewed_query)
        most_viewed = [
            {
                "id": row.id,
                "title": row.title,
                "view_count": row.view_count,
                "download_count": row.download_count,
                "average_rating": float(row.average_rating) if row.average_rating else 0.0,
            }
            for row in most_viewed_result
        ]

        most_rated_query = text("""
            SELECT id, title, average_rating, rating_count
            FROM menu_items 
            WHERE is_active = true AND rating_count > 0
            ORDER BY average_rating DESC, rating_count DESC 
            LIMIT 10
        """)
        most_rated_result = await db.execute(most_rated_query)
        most_rated = [
            {
                "id": row.id,
                "title": row.title,
                "average_rating": float(row.average_rating) if row.average_rating else 0.0,
                "rating_count": row.rating_count,
            }
            for row in most_rated_result
        ]

        return {
            "total_menu_items": total_menu_items or 0,
            "most_viewed": most_viewed,
            "most_rated": most_rated,
        }

    async def get_activities_statistics(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Получить статистику активностей.

        Args:
            db: Сессия базы данных
            start_date: Начальная дата фильтрации
            end_date: Конечная дата фильтрации

        Returns:
            Словарь со статистикой активностей
        """
        date_filter = ""
        if start_date and end_date:
            date_filter = f"WHERE created_at >= '{start_date.isoformat()}' AND created_at <= '{end_date.isoformat()}'"
        elif start_date:
            date_filter = f"WHERE created_at >= '{start_date.isoformat()}'"
        elif end_date:
            date_filter = f"WHERE created_at <= '{end_date.isoformat()}'"

        total_stats_query = text(f"""
            SELECT 
                COUNT(*) FILTER (WHERE activity_type = 'navigation') as total_views,
                COUNT(*) FILTER (WHERE activity_type = 'pdf_download') as total_downloads,
                COUNT(*) FILTER (WHERE activity_type = 'rating') as total_ratings,
                COUNT(*) FILTER (WHERE activity_type = 'search') as total_searches
            FROM user_activities 
            {date_filter}
        """)
        stats_result = await db.execute(total_stats_query)
        stats_row = stats_result.first()

        popular_searches_query = text(f"""
            SELECT search_query, COUNT(*) as count 
            FROM user_activities 
            WHERE activity_type = 'search' AND search_query IS NOT NULL {date_filter.replace('created_at', 'created_at') if date_filter else ''}
            GROUP BY search_query 
            ORDER BY count DESC 
            LIMIT 10
        """)
        searches_result = await db.execute(popular_searches_query)
        search_queries = [{"query": row.search_query, "count": row.count} for row in searches_result]

        return {
            "total_views": stats_row.total_views or 0,
            "total_downloads": stats_row.total_downloads or 0,
            "total_ratings": stats_row.total_ratings or 0,
            "total_searches": stats_row.total_searches or 0,
            "search_queries": search_queries,
        }

    async def get_questions_statistics(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """Получить статистику по вопросам.

        Args:
            db: Сессия базы данных
            start_date: Начальная дата фильтрации
            end_date: Конечная дата фильтрации

        Returns:
            Словарь со статистикой вопросов
        """
        date_filter = ""
        if start_date and end_date:
            date_filter = f"WHERE created_at >= '{start_date.isoformat()}' AND created_at <= '{end_date.isoformat()}'"
        elif start_date:
            date_filter = f"WHERE created_at >= '{start_date.isoformat()}'"
        elif end_date:
            date_filter = f"WHERE created_at <= '{end_date.isoformat()}'"

        status_stats_query = text(f"""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'pending') as pending,
                COUNT(*) FILTER (WHERE status = 'answered') as answered
            FROM user_questions 
            {date_filter}
        """)
        status_result = await db.execute(status_stats_query)
        status_row = status_result.first()

        return {
            "total": status_row.total or 0,
            "pending": status_row.pending or 0,
            "answered": status_row.answered or 0,
        }


analytics_crud = AnalyticsCRUD()
