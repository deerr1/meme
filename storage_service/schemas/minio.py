from pydantic import BaseModel, Field


class PutImageResponse(BaseModel):
    image_url: str = Field(
        description='URL изображения из хранилища'
    )
    image_name: str = Field(
        description='Название изображения(является идентификатором в хранилище)'
    )