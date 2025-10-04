"""Базовый CRUD класс с общими операциями."""

from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD операций."""

    def __init__(self, model: Type[ModelType]):
        """CRUD объект с методами для создания, чтения, обновления и удаления.

        Args:
            model: SQLAlchemy модель
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Получить объект по ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить список объектов с пагинацией."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """Создать новый объект."""
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.model_dump(exclude_unset=True)

        db_obj = self.model(**obj_in_data)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Обновить объект."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """Удалить объект."""
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def count(self, db: AsyncSession) -> int:
        """Подсчитать общее количество объектов."""
        result = await db.execute(select(func.count(self.model.id)))
        return result.scalar() or 0
