import pytest
from pytest_mock import MockerFixture
from aiobotocore.session import AioSession

from services.minio import get_minio_service, MinIOService
from schemas.minio import PutImageResponse


service: MinIOService = get_minio_service(access_key_id='key', secret_access_key='key')

@pytest.mark.anyio
async def test_update_image(mocker: MockerFixture):
    file_name = 'file_name'
    file = bytes()
    image_url = f'{service.config["endpoint_url"]}/{service.bucket_name}/{file_name}'
    expected_result= PutImageResponse(image_name=file_name, image_url=image_url)

    client_mock = mocker.MagicMock()
    mocker.patch.object(AioSession, 'create_client', return_value=client_mock)

    result = await service.upload_file(file_name, file)

    assert result == expected_result

@pytest.mark.anyio
async def test_remove_image(mocker: MockerFixture):
    file_name = 'file_name'

    client_mock = mocker.MagicMock()
    mocker.patch.object(AioSession, 'create_client', return_value=client_mock)

    result = await service.remove_file(file_name)

    assert result == file_name