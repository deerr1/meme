from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import HTTPException
from aiobotocore.session import get_session
from botocore.exceptions import ClientError

from core.settings import settings, Settings
from schemas.minio import PutImageResponse


class MinIOService:
    def __init__(self, settings: Settings, access_key_id: str, secret_access_key: str):
        self.config = {
            'aws_access_key_id': access_key_id,
            'aws_secret_access_key': secret_access_key,
            'endpoint_url': settings.MINIO_EDNPOINT
        }
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        try:
            async with  self.session.create_client('s3', **self.config) as client:
                yield client
        except ClientError as exc:
            if exc.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                raise HTTPException(status_code=404, detail='Изображение не найдено')
            if exc.response['ResponseMetadata']['HTTPStatusCode'] == 403:
                raise HTTPException(status_code=403, detail='Неправильные авторизационные данные')

    async def get_file(self, file_name: str) -> bytes:
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=file_name)
            async with response['Body'] as stream:
                file = await stream.read()
            return file

    async def upload_file(self, file_name: str, file: bytes) -> PutImageResponse:
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file
            )
        image_url = f'{self.config["endpoint_url"]}/{self.bucket_name}/{file_name}'

        return PutImageResponse(image_name=file_name, image_url=image_url)

    async def remove_file(self, file_name: str) -> str:
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=file_name
            )

        return file_name


@lru_cache
def get_minio_service(access_key_id:str, secret_access_key: str):
    return MinIOService(settings=settings, access_key_id=access_key_id, secret_access_key=secret_access_key)