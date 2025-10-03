"""CRUD операции для аналитики системы."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import MenuItem, TelegramUser, UserActivity, UserQuestion
from backend.models.enums import ActivityType


class AnalyticsCRUD:
    """CRUD для аналитических запросов и статистики.

    - ORM для простых запросов (COUNT, базовые фильтры)
    - SQL для сложной аналитики (агрегации, FILTER, оконные функции)
    """

    def __init__(self):
        """Инициализация AnalyticsCRUD."""

    def _create_date_filters(self, start_date: Optional[datetime], end_date: Optional[datetime]):
        """Создать фильтры по датам для использования в запросах.

        Args:
            start_date: Начальная дата фильтрации
            end_date: Конечная дата фильтрации

        Returns:
            Список условий для фильтрации по датам
        """
        filters = []
        if start_date:
            filters.append(True)  # Placeholder - будет заменен в конкретных методах
        if end_date:
            filters.append(True)  # Placeholder - будет заменен в конкретных методах
        return filters

    def _apply_date_conditions(self, query, date_field, start_date: Optional[datetime], end_date: Optional[datetime]):
        """Применить условия фильтрации по датам к запросу.

        Args:
            query: SQLAlchemy query объект
            date_field: Поле даты для фильтрации
            start_date: Начальная дата
            end_date: Конечная дата

        Returns:
            Модифицированный query с примененными фильтрами дат
        """
        if start_date:
            query = query.where(date_field >= start_date)
        if end_date:
            query = query.where(date_field <= end_date)
        return query

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
        now_utc = datetime.now(timezone.utc)

        # Общее количество пользователей
        total_query = select(func.count(TelegramUser.id))
        if start_date and end_date:
            # Если указан диапазон дат, считаем пользователей в этом диапазоне
            total_query = self._apply_date_conditions(total_query, TelegramUser.created_at, start_date, end_date)
        elif start_date:
            total_query = self._apply_date_conditions(total_query, TelegramUser.created_at, start_date, None)
        elif end_date:
            total_query = self._apply_date_conditions(total_query, TelegramUser.created_at, None, end_date)

        total_result = await db.execute(total_query)
        total = total_result.scalar()

        # Активные пользователи сегодня
        today_start = datetime.combine(date.today(), datetime.min.time(), timezone.utc)
        today_query = select(func.count(TelegramUser.id)).where(TelegramUser.last_activity >= today_start)
        today_result = await db.execute(today_query)
        active_today = today_result.scalar()

        # Активные пользователи за неделю
        week_ago = now_utc - timedelta(days=7)
        week_query = select(func.count(TelegramUser.id)).where(
            and_(TelegramUser.last_activity >= week_ago, TelegramUser.last_activity.is_not(None))
        )
        week_result = await db.execute(week_query)
        active_week = week_result.scalar()

        # Активные пользователи за месяц
        month_ago = now_utc - timedelta(days=30)
        month_query = select(func.count(TelegramUser.id)).where(
            and_(TelegramUser.last_activity >= month_ago, TelegramUser.last_activity.is_not(None))
        )
        month_result = await db.execute(month_query)
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
        # Общее количество активных элементов меню
        total_query = select(func.count(MenuItem.id)).where(MenuItem.is_active)
        if start_date or end_date:
            total_query = self._apply_date_conditions(total_query, MenuItem.created_at, start_date, end_date)

        total_items_result = await db.execute(total_query)
        total_menu_items = total_items_result.scalar()

        # Наиболее просматриваемые элементы
        most_viewed_query = select(
            MenuItem.id, MenuItem.title, MenuItem.view_count, MenuItem.download_count, MenuItem.average_rating
        ).where(MenuItem.is_active)

        if start_date or end_date:
            most_viewed_query = self._apply_date_conditions(
                most_viewed_query, MenuItem.created_at, start_date, end_date
            )

        most_viewed_query = most_viewed_query.order_by(MenuItem.view_count.desc()).limit(10)
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

        # Наиболее рейтинговые элементы
        most_rated_query = select(MenuItem.id, MenuItem.title, MenuItem.average_rating, MenuItem.rating_count).where(
            MenuItem.is_active, MenuItem.rating_count > 0
        )

        if start_date or end_date:
            most_rated_query = self._apply_date_conditions(most_rated_query, MenuItem.created_at, start_date, end_date)

        most_rated_query = most_rated_query.order_by(
            MenuItem.average_rating.desc(), MenuItem.rating_count.desc()
        ).limit(10)
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
        # Базовый запрос для статистики активностей
        base_query = select(
            func.count().filter(UserActivity.activity_type == ActivityType.TEXT_VIEW).label("text_views"),
            func.count().filter(UserActivity.activity_type == ActivityType.IMAGE_VIEW).label("image_views"),
            func.count().filter(UserActivity.activity_type == ActivityType.VIDEO_VIEW).label("video_views"),
            func.count().filter(UserActivity.activity_type == ActivityType.PDF_DOWNLOAD).label("pdf_downloads"),
            func.count().filter(UserActivity.activity_type == ActivityType.MEDIA_VIEW).label("media_views"),
            func.count().filter(UserActivity.activity_type == ActivityType.RATING).label("ratings"),
            func.count().filter(UserActivity.activity_type == ActivityType.SEARCH).label("searches"),
            func.count().filter(UserActivity.activity_type == ActivityType.NAVIGATION).label("navigation"),
        ).select_from(UserActivity)

        # Применяем фильтры по датам
        if start_date or end_date:
            base_query = self._apply_date_conditions(base_query, UserActivity.created_at, start_date, end_date)

        stats_result = await db.execute(base_query)
        stats_row = stats_result.first()

        # Популярные поисковые запросы
        searches_query = select(UserActivity.search_query, func.count().label("count")).where(
            UserActivity.activity_type == ActivityType.SEARCH, UserActivity.search_query.is_not(None)
        )

        if start_date or end_date:
            searches_query = self._apply_date_conditions(searches_query, UserActivity.created_at, start_date, end_date)

        searches_query = searches_query.group_by(UserActivity.search_query).order_by(func.count().desc()).limit(10)
        searches_result = await db.execute(searches_query)

        search_queries = [{"query": row.search_query, "count": row.count} for row in searches_result]

        return {
            "total_views": (stats_row.text_views or 0)
            + (stats_row.image_views or 0)
            + (stats_row.video_views or 0)
            + (stats_row.media_views or 0)
            + (stats_row.navigation or 0),
            "total_downloads": stats_row.pdf_downloads or 0,
            "total_ratings": stats_row.ratings or 0,
            "total_searches": stats_row.searches or 0,
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
        # Запрос статистики по статусам вопросов
        status_query = select(
            func.count().label("total"),
            func.count().filter(UserQuestion.status == "pending").label("pending"),
            func.count().filter(UserQuestion.status == "answered").label("answered"),
            func.count().filter(UserQuestion.status == "closed").label("closed"),
        ).select_from(UserQuestion)

        # Применяем фильтры по датам
        if start_date or end_date:
            status_query = self._apply_date_conditions(status_query, UserQuestion.created_at, start_date, end_date)

        status_result = await db.execute(status_query)
        status_row = status_result.first()

        return {
            "total": status_row.total or 0,
            "pending": status_row.pending or 0,
            "answered": status_row.answered or 0,
        }


analytics_crud = AnalyticsCRUD()
