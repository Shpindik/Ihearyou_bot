"""Публичные эндпоинты для работы с меню."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.exceptions import IHearYouException, NotFoundError, ValidationError
from backend.schemas.public.menu import MenuContentResponse, MenuItemListResponse
from backend.services.menu_item import menu_item_service


router = APIRouter(prefix="/menu-items", tags=["Public Menu"])


@router.get(
    "/",
    response_model=MenuItemListResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение структуры меню",
    description="Возвращает структуру меню для пользователя с возможностью фильтрации по родительскому элементу",
    responses={
        200: {"description": "Структура меню успешно получена"},
        400: {"description": "Ошибка валидации параметров запроса"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_menu_items(
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram"),
    parent_id: Optional[int] = Query(None, description="ID родительского пункта меню (null для корневого уровня)"),
    db: AsyncSession = Depends(get_session),
) -> MenuItemListResponse:
    """Получение пунктов меню для пользователя (один уровень).

    Пользователь должен быть зарегистрирован через Bot API.
    Возвращает только один уровень меню для простоты MVP.
    """
    try:
        return await menu_item_service.get_menu_items(telegram_user_id=telegram_user_id, parent_id=parent_id, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при получении меню"
        )
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


@router.get(
    "/{id}/content",
    response_model=MenuContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение контента пункта меню",
    description="Возвращает полный контент конкретного пункта меню включая файлы и дочерние элементы",
    responses={
        200: {"description": "Контент пункта меню успешно получен"},
        400: {"description": "Ошибка валидации параметров запроса"},
        403: {"description": "Недостаточно прав для доступа к контенту"},
        404: {"description": "Пользователь или пункт меню не найден"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)
async def get_menu_item_content(
    id: int,
    telegram_user_id: int = Query(..., description="ID пользователя в Telegram"),
    db: AsyncSession = Depends(get_session),
) -> MenuContentResponse:
    """Получение контента конкретного пункта меню с дочерними элементами.

    Проверяет права доступа пользователя к контенту.
    Возвращает контент и прямых дочерних элементов.
    """
    try:
        return await menu_item_service.get_menu_item_content(menu_id=id, telegram_user_id=telegram_user_id, db=db)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        # Проверяем тип ошибки для корректного маппирования статус-кода
        error_message = str(e)
        if "доступ" in error_message.lower() or "премиум" in error_message.lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_message)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка базы данных при получении контента"
        )
    except IHearYouException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")
