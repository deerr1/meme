from typing import Generic, TypeVar, Any

from pydantic import BaseModel
from sqlalchemy import select, delete, func
from fastapi.encoders import jsonable_encoder

from db.database import get_session
from db.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: ModelType):
        self.model = model

    async def get(self, id: Any) -> ModelType | None:
        async with get_session() as session:
            db_obj = await session.execute(
                select(self.model).filter(self.model.id == id)
            )
            return db_obj.scalars().first()

    async def get_multi(self, *, offset:int=0,limit:int=100) -> list[ModelType]:
        async with get_session() as session:
            db_obj = await session.execute(
                select(self.model).order_by(self.model.created_datetime.desc()).offset(offset).limit(limit)
            )
            return db_obj.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        async with get_session() as session:
            db_obj = self.model(**obj_in.dict())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        async with get_session() as session:
            obj_data = jsonable_encoder(obj_in)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)
            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    async def remove(self, id: Any) -> Any:
        async with get_session() as session:
            await session.execute(delete(self.model).filter(self.model.id == id))
            await session.commit()
            return id

    async def count(self) -> int:
        async with get_session() as session:
            count = await session.execute(
                select(func.count()).select_from(self.model)
            )
            return count.scalars().first()