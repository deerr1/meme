from typing import Annotated
from uuid import UUID, uuid4

import fastapi

from db.repositories.meme import get_meme_rep, MemeRepository
from schemas.meme import CRUDMeme, PaginationMeme
from services.storage import get_storage_service, StorageService
from core.settings import settings


router = fastapi.APIRouter(tags=['memes'])


@router.get('/memes')
async def get_memes(
    page: Annotated[int, fastapi.Query(ge=1)]=1,
    size: Annotated[int, fastapi.Query(ge=1)]=50,
    repository: MemeRepository=fastapi.Depends(get_meme_rep)
) -> PaginationMeme:
    count = await repository.count()

    if count == 0:
        raise fastapi.HTTPException(status_code=404, detail='Мемов нет')

    skip_items = (page - 1) * size
    total_pages = (count // size) + (count % size > 0)

    if page > total_pages:
        raise fastapi.HTTPException(status_code=400, detail='Номер страницы превышает доступное количество')
    list_meme = await repository.get_multi(offset=skip_items, limit=size)
    response = PaginationMeme(
        list_meme=list_meme,
        total_pages=total_pages,
        page=page,
        size=size
    )
    return response

@router.get('/memes/{id}')
async def get_meme(
    id: Annotated[UUID, fastapi.Path(title='Идентификатор мема')],
    repository: MemeRepository=fastapi.Depends(get_meme_rep)
) -> CRUDMeme:
    meme = await repository.get(id)
    if not meme:
        raise fastapi.HTTPException(status_code=404, detail='Мем не найден')
    return meme

@router.post('/memes')
async def create_meme(
    description: Annotated[str, fastapi.Form(description='Описание мема')],
    image: Annotated[fastapi.UploadFile, fastapi.File(description='Файл изображения мема')],
    repository: MemeRepository=fastapi.Depends(get_meme_rep),
    storage: StorageService=fastapi.Depends(get_storage_service)
) -> CRUDMeme:
    try:
        file = await image.read()
        filename = f'{uuid4().hex}:{image.filename}'
        image_name = await storage.put_image(filename, file)
        image_url = f'{settings.SERVICE_IMAGE_ROUTE}{image_name}'
    finally:
        await image.close()
    meme = CRUDMeme(description=description, image_url=image_url, image_name=image_name)
    meme = await repository.create(meme)
    return meme

@router.put('/memes/{id}')
async def update_meme(
    id: Annotated[UUID, fastapi.Path(title='Идентификатор мема')],
    description: Annotated[str | None, fastapi.Form(description='Описание мема')]=None,
    image: Annotated[fastapi.UploadFile | None, fastapi.File(description='Файл изображения мема')]=None,
    repository: MemeRepository=fastapi.Depends(get_meme_rep),
    storage: StorageService=fastapi.Depends(get_storage_service)
) -> CRUDMeme:
    meme = await repository.get(id)
    if not meme:
        raise fastapi.HTTPException(status_code=404, detail='Мем не найден')
    if image:
        try:
            file = await image.read()
            image_name = await storage.put_image(meme.image_name, file)
            image_url = f'{settings.SERVICE_IMAGE_ROUTE}{image_name}'
        finally:
            await image.close()
    else:
        image_url, image_name = meme.image_url, meme.image_name
    if not description:
        description = meme.description
    meme_in = CRUDMeme(description=description, image_url=image_url, image_name=image_name)
    meme = await repository.update(db_obj=meme, obj_in=meme_in)
    return meme

@router.delete('/memes/{id}')
async def delete_meme(
    id: Annotated[UUID, fastapi.Path(title='Идентификатор мема')],
    repository: MemeRepository=fastapi.Depends(get_meme_rep),
    storage: StorageService=fastapi.Depends(get_storage_service)
)->fastapi.Response:
    meme = await repository.get(id)
    if not meme:
        raise fastapi.HTTPException(status_code=404, detail='Мем не найден')
    await storage.remove_file(meme.image_name)
    await repository.remove(id)
    return fastapi.Response(status_code=200)

@router.get('/images/{image_name}')
async def get_image(
    image_name: Annotated[str, fastapi.Path(description='Название изображения')],
    storage: StorageService=fastapi.Depends(get_storage_service)
) -> fastapi.Response:
    image = await storage.get_image(image_name)
    return fastapi.Response(content=image, media_type='image/*')
