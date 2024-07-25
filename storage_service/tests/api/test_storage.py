import pytest
from pytest_mock import MockerFixture
from httpx import AsyncClient, ASGITransport, BasicAuth
from botocore.exceptions import ClientError
from aiobotocore.session import AioSession
from botocore.exceptions import ClientError

from main import app
from services.minio import MinIOService
from schemas.minio import PutImageResponse


@pytest.mark.anyio
async def test_get_image_200(mocker: MockerFixture):
    auth = BasicAuth(username='user', password='pass')

    mocker.patch.object(MinIOService, 'get_file', return_value=bytes())
    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1", auth=auth,) as client:
        response = await client.get(f"/images/{'file_name'}")
    assert response.status_code == 200

@pytest.mark.anyio
async def test_get_image_404(mocker: MockerFixture):
    auth = BasicAuth(username='user', password='pass')
    exc = {'ResponseMetadata': {'HTTPStatusCode': 404}}

    mocker.patch.object(AioSession, 'create_client', side_effect=ClientError(exc, ''))

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1", auth=auth,) as client:
        response = await client.get(f"/images/{'file_name'}")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_put_image_200(mocker: MockerFixture):
    auth = BasicAuth(username='user', password='pass')

    put_response = PutImageResponse(image_name='file_name', image_url='image_url')
    mocker.patch.object(MinIOService, 'upload_file', return_value=put_response)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1", auth=auth,) as client:
        file = {'file': ('file name', bytes())}
        response = await client.put('/images', files=file)
    assert response.status_code == 200

@pytest.mark.anyio
async def test_put_image_403(mocker: MockerFixture):
    auth = BasicAuth(username='incorrect_user', password='incorrect_pass')
    exc = {'ResponseMetadata': {'HTTPStatusCode': 403}}

    mocker.patch.object(AioSession, 'create_client', side_effect=ClientError(exc, ''))

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1", auth=auth,) as client:
        file = {'file': ('file name', bytes())}
        response = await client.put('/images', files=file)
    assert response.status_code == 403

@pytest.mark.anyio
async def test_delete_image_200(mocker: MockerFixture):
    file_name = 'file_name'
    auth = BasicAuth(username='user', password='pass')

    mocker.patch.object(MinIOService, 'remove_file', return_value=file_name)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1", auth=auth,) as client:
        file = {'file': ('file name', bytes())}
        response = await client.delete(f'/images/{file_name}')
    assert response.status_code == 200

