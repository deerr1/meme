import pytest
from pytest_mock import MockerFixture
from httpx import AsyncClient
from fastapi import HTTPException

from services.storage import get_storage_service, StorageService


service: StorageService = get_storage_service()


@pytest.mark.anyio
async def test_get_image(mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.content = bytes()

    mocker.patch.object(AsyncClient, 'get', return_value=mock_response)

    image_name = 'name'
    image = bytes()
    result = await service.get_image(image_name)

    assert result == image

@pytest.mark.anyio
async def test_get_image_raise_404(mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.content = bytes()

    mocker.patch.object(AsyncClient, 'get', return_value=mock_response)

    image_name = 'name'
    with pytest.raises(HTTPException) as exc:
        await service.get_image(image_name)

    assert exc.value.status_code == 404

@pytest.mark.anyio
async def test_get_image_raise_500(mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_response.content = bytes()

    mocker.patch.object(AsyncClient, 'get', return_value=mock_response)

    image_name = 'name'
    with pytest.raises(HTTPException) as exc:
        await service.get_image(image_name)

    assert exc.value.status_code == 500

@pytest.mark.anyio
async def test_put_image(mocker: MockerFixture):
    data = {'image_url': 'some url', 'image_name': 'some name'}
    mock_response = mocker.Mock()
    mock_response.json.return_value = data
    mock_response.status_code = 200

    mocker.patch.object(AsyncClient, 'put', return_value=mock_response)

    file_name = 'name'
    image = bytes()
    result = await service.put_image(file_name, image)

    assert result == data.get('image_name')

@pytest.mark.anyio
async def test_put_image_raise_500(mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.status_code = 500

    mocker.patch.object(AsyncClient, 'put', return_value=mock_response)

    file_name = 'name'
    image = bytes()
    with pytest.raises(HTTPException) as exc:
        await service.put_image(file_name, image)
    assert exc.value.status_code == 500

@pytest.mark.anyio
async def test_remove_image(mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mocker.patch.object(AsyncClient, 'delete', return_value=mock_response)

    file_name = 'name'
    result = await service.remove_file(file_name)

    assert result == 200

@pytest.mark.anyio
async def test_remove_image_raise_500(mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mocker.patch.object(AsyncClient, 'delete', return_value=mock_response)

    file_name = 'name'

    with pytest.raises(HTTPException) as exc:
        await service.remove_file(file_name)
    assert exc.value.status_code == 500