from functools import lru_cache

from fastapi import HTTPException
from httpx import AsyncClient, BasicAuth, Response

from core.settings import settings, Settings



class StorageService:
    def __init__(self, settings: Settings):
        self.get_route = f'{settings.STORAGE_ENDPOINT}{settings.STORAGE_GET_ROUTE}'
        self.put_route = f'{settings.STORAGE_ENDPOINT}{settings.STORAGE_PUT_ROUTE}'
        self.delete_route = f'{settings.STORAGE_ENDPOINT}{settings.STORAGE_DELETE_ROUTE}'
        self.auth = BasicAuth(username=settings.STORAGE_USERNAME, password=settings.STORAGE_PASSWORD)

    async def get_image(self, file_name: str) -> bytes:
        async with AsyncClient(auth=self.auth) as client:
            url =  f'{self.get_route}{file_name}'
            response = await client.get(url)
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail='Изображение не найдено')
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail='Неполадки в работе')
            return response.content

    async def put_image(self, file_name: str, image: bytes) -> str:
        async with AsyncClient(auth=self.auth) as client:
            file = {'file': (file_name, image)}
            response = await client.put(self.put_route, files=file)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail='Неполадки в работе')
            data = response.json()
            image_name = data.get('image_name')
            return image_name


    async def remove_file(self, image_name: str) -> int:
        async with AsyncClient(auth=self.auth) as client:
            response = await client.delete(self.delete_route+f'{image_name}')
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail='Неполадки в работе')
            return response.status_code


@lru_cache
def get_storage_service():
    return StorageService(settings)