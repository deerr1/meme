import uuid

import pytest
from pytest_mock import MockerFixture
from httpx import AsyncClient, ASGITransport

from main import app
from db.repositories.meme import  MemeRepository
from services.storage import StorageService
from schemas.meme import CRUDMeme


meme = CRUDMeme(id=uuid.uuid4(), description='description', image_url='image_url', image_name='image_name')


@pytest.mark.anyio
async def test_get_memes_200(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'count', return_value=2)
    mocker.patch.object(MemeRepository, 'get_multi', return_value=[meme, meme])

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get('/memes')
    assert response.status_code == 200

@pytest.mark.anyio
async def test_get_memes_total_pages(mocker: MockerFixture):
    total_pages = 2
    size = 25

    mocker.patch.object(MemeRepository, 'count', return_value=total_pages*size)
    mocker.patch.object(MemeRepository, 'get_multi', return_value=[meme, meme])

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get(f'/memes?size={size}')
    assert response.json()['total_pages'] == total_pages

@pytest.mark.anyio
async def test_get_memes_404(mocker: MockerFixture):

    mocker.patch.object(MemeRepository, 'count', return_value=0)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get('/memes')
    assert response.status_code == 404

@pytest.mark.anyio
async def test_get_memes_400(mocker: MockerFixture):
    page = 999

    mocker.patch.object(MemeRepository, 'count', return_value=2)
    mocker.patch.object(MemeRepository, 'get_multi', return_value=[meme, meme])

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get(f'/memes?page={page}')
    assert response.status_code == 400

@pytest.mark.anyio
async def test_get_mem_200(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'get', return_value=meme)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get(f'/memes/{meme.id}')
    assert response.status_code == 200

@pytest.mark.anyio
async def test_get_mem_404(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'get', return_value=None)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get(f'/memes/{meme.id}')
    assert response.status_code == 404

@pytest.mark.anyio
async def test_post_meme_200(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'create', return_value=meme)
    mocker.patch.object(StorageService, 'put_image', return_value='image_name')

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        data = {'description': 'some description'}
        file = {'image': ('file name', bytes())}
        response = await client.post('/memes', data=data, files=file)
    assert response.status_code == 200

@pytest.mark.anyio
async def test_post_meme_500(mocker: MockerFixture):
    response_mock = mocker.Mock()
    response_mock.status_code = 500

    client_mock = mocker.AsyncMock()
    client_mock.get.return_value = response_mock

    manager_mock = mocker.MagicMock()
    manager_mock.return_value.__aenter__.return_value = client_mock

    mocker.patch('services.storage.AsyncClient', new=manager_mock)
    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        data = {'description': 'some description'}
        file = {'image': ('file name', bytes())}
        response = await client.post('/memes', data=data, files=file)
    assert response.status_code == 500

@pytest.mark.anyio
async def test_put_meme_200(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'get', return_value=meme)
    mocker.patch.object(StorageService, 'put_image', return_value='image_name')
    mocker.patch.object(MemeRepository, 'update', return_value=meme)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        data = {'description': 'some description'}
        file = {'image': ('file name', bytes())}
        response = await client.put(f'/memes/{meme.id}',data=data, files=file)
    assert response.status_code == 200

@pytest.mark.anyio
async def test_put_meme_404(mocker):
    mocker.patch.object(MemeRepository, 'get', return_value=None)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        data = {'description': 'some description'}
        file = {'image': ('file name', bytes())}
        response = await client.put(f'/memes/{meme.id}',data=data, files=file)
    assert response.status_code == 404

@pytest.mark.anyio
async def test_put_meme_500(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'get', return_value=meme)
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mocker.patch.object(AsyncClient, 'put', return_value=mock_response)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        data = {'description': 'some description'}
        file = {'image': ('file name', bytes())}
        response = await client.put(f'/memes/{meme.id}',data=data, files=file)
    assert response.status_code == 500

@pytest.mark.anyio
async def test_delete_meme_200(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'get', return_value=meme)
    mocker.patch.object(StorageService, 'remove_file', return_value=200)
    mocker.patch.object(MemeRepository, 'remove', return_value=meme.id)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.delete(f'/memes/{meme.id}')
    assert response.status_code == 200

@pytest.mark.anyio
async def test_delete_meme_404(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'get', return_value=None)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.delete(f'/memes/{meme.id}')
    assert response.status_code == 404

@pytest.mark.anyio
async def test_delete_meme_500(mocker: MockerFixture):
    mocker.patch.object(MemeRepository, 'get', return_value=meme)

    response_mock = mocker.Mock()
    response_mock.status_code = 500

    client_mock = mocker.AsyncMock()
    client_mock.delete.return_value = response_mock

    manager_mock = mocker.MagicMock()
    manager_mock.return_value.__aenter__.return_value = client_mock

    mocker.patch('services.storage.AsyncClient', new=manager_mock)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.delete(f'/memes/{meme.id}')
    assert response.status_code == 500

@pytest.mark.anyio
async def test_get_image_200(mocker: MockerFixture):
    mocker.patch.object(StorageService, 'get_image', return_value=bytes())

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get('/file_name')
    assert response.status_code == 200

@pytest.mark.anyio
async def test_get_image_404(mocker: MockerFixture):
    response_mock = mocker.Mock()
    response_mock.status_code = 404

    client_mock = mocker.AsyncMock()
    client_mock.get.return_value = response_mock

    manager_mock = mocker.MagicMock()
    manager_mock.return_value.__aenter__.return_value = client_mock

    mocker.patch('services.storage.AsyncClient', new=manager_mock)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get('/file_name')
    assert response.status_code == 404

@pytest.mark.anyio
async def test_get_image_500(mocker: MockerFixture):
    response_mock = mocker.Mock()
    response_mock.status_code = 500

    client_mock = mocker.AsyncMock()
    client_mock.get.return_value = response_mock

    manager_mock = mocker.MagicMock()
    manager_mock.return_value.__aenter__.return_value = client_mock

    mocker.patch('services.storage.AsyncClient', new=manager_mock)

    async with AsyncClient(transport=ASGITransport(app=app, client=('localhost', '8000')), base_url="http://localhost:8000/api/v1") as client:
        response = await client.get('/file_name')
    assert response.status_code == 500
