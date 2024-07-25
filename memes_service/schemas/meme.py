from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class BaseMeme(BaseModel):
    id: UUID | None = Field(
        description='Идентификатор записи',
        default=None
    )


class CRUDMeme(BaseMeme):
    model_config = ConfigDict(from_attributes=True)

    description: str = Field(
        description='Описание мема'
    )
    image_url: str = Field(
        description='Ссылка на изображение'
    )
    image_name: str = Field(
        description='Название изображения'
    )

class PaginationMeme(BaseModel):
    list_meme: list[CRUDMeme] = Field(
        description='Список мемов'
    )
    total_pages: int = Field(
        description='Общее количество страниц'
    )
    page: int = Field(
        description='Номер текущей страницы'
    )
    size: int = Field(
        description='Количество элементов на странице'
    )