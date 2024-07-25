from typing import Annotated

import fastapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from services.minio import get_minio_service, MinIOService
from schemas.minio import PutImageResponse
from core.settings import settings


router = fastapi.APIRouter(tags=['storage'])

security= HTTPBasic()

async def get_minio_by_user(credentials: Annotated[HTTPBasicCredentials, fastapi.Depends(security)]) -> MinIOService:
    access_key_id = credentials.username
    secret_access_key = credentials.password
    minio = get_minio_service(access_key_id ,secret_access_key)
    return minio

@router.get('/images/{file_name}')
async def get_image(
    file_name: Annotated[str, fastapi.Path()],
    minio: MinIOService=fastapi.Depends(get_minio_by_user)
) -> fastapi.Response:
    file = await minio.get_file(file_name)
    return fastapi.Response(content=file, media_type='image/*')


@router.put('/images')
async def update_image(
    file: Annotated[fastapi.UploadFile, fastapi.File(description='Файл изображения')],
    minio: MinIOService=fastapi.Depends(get_minio_by_user)
) -> PutImageResponse:
    try:
        image = await file.read()
    finally:
        await file.close()
    response = await minio.upload_file(file.filename, image)

    return response

@router.delete('/images/{image_name}')
async def delete_image(
    image_name: Annotated[str, fastapi.Path(description='Идентификатор изображения')],
    minio: MinIOService=fastapi.Depends(get_minio_by_user)
) -> fastapi.Response:
    await minio.remove_file(image_name)
    return fastapi.Response(status_code=200)