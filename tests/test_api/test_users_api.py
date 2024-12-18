from builtins import str
import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user_model import User, UserRole
from app.utils.nickname_gen import generate_nickname
from app.utils.security import hash_password
from app.services.jwt_service import decode_token  # Import your FastAPI app
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import status

# Example of a test function using the async_client fixture
@pytest.mark.asyncio
async def test_create_user_access_denied(async_client, user_token, email_service):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Define user data for the test
    user_data = {
        "nickname": generate_nickname(),
        "email": "test@example.com",
        "password": "sS#fdasrongPassword123!",
    }
    # Send a POST request to create a user
    response = await async_client.post("/users/", json=user_data, headers=headers)
    # Asserts
    assert response.status_code == 403

# You can similarly refactor other test functions to use the async_client fixture
@pytest.mark.asyncio
async def test_retrieve_user_access_denied(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get(f"/users/{verified_user.id}", headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_retrieve_user_access_allowed(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == str(admin_user.id)

@pytest.mark.asyncio
async def test_update_user_email_access_denied(async_client, verified_user, user_token):
    updated_data = {"email": f"updated_{verified_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(f"/users/{verified_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_user_email_access_allowed(async_client, admin_user, admin_token):
    updated_data = {"email": f"updated_{admin_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == updated_data["email"]


@pytest.mark.asyncio
async def test_delete_user(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/users/{admin_user.id}", headers=headers)
    assert delete_response.status_code == 204
    # Verify the user is deleted
    fetch_response = await async_client.get(f"/users/{admin_user.id}", headers=headers)
    assert fetch_response.status_code == 404

@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client, verified_user):
    user_data = {
        "email": verified_user.email,
        "password": "AnotherPassword123!",
        "role": UserRole.ADMIN.name
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "Email already exists" in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_create_user_invalid_email(async_client):
    user_data = {
        "email": "notanemail",
        "password": "ValidPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 422

import pytest
from app.services.jwt_service import decode_token
from urllib.parse import urlencode

@pytest.mark.asyncio
async def test_login_success(async_client, verified_user):
    # Attempt to login with the test user
    form_data = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    # Check for successful login response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Use the decode_token method from jwt_service to decode the JWT
    decoded_token = decode_token(data["access_token"])
    assert decoded_token is not None, "Failed to decode token"
    assert decoded_token["role"] == "AUTHENTICATED", "The user role should be AUTHENTICATED"

@pytest.mark.asyncio
async def test_login_user_not_found(async_client):
    form_data = {
        "username": "nonexistentuser@here.edu",
        "password": "DoesNotMatter123!"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401
    assert "Incorrect email or password." in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "IncorrectPassword123!"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401
    assert "Incorrect email or password." in response.json().get("detail", "")

@pytest.mark.asyncio
async def test_login_unverified_user(async_client, unverified_user):
    form_data = {
        "username": unverified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_login_locked_user(async_client, locked_user):
    form_data = {
        "username": locked_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 400
    assert "Account locked due to too many failed login attempts." in response.json().get("detail", "")
@pytest.mark.asyncio
async def test_delete_user_does_not_exist(async_client, admin_token):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"  # Valid UUID format
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/users/{non_existent_user_id}", headers=headers)
    assert delete_response.status_code == 404

@pytest.mark.asyncio
async def test_update_user_github(async_client, admin_user, admin_token):
    updated_data = {"github_profile_url": "http://www.github.com/kaw393939"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["github_profile_url"] == updated_data["github_profile_url"]

@pytest.mark.asyncio
async def test_update_user_linkedin(async_client, admin_user, admin_token):
    updated_data = {"linkedin_profile_url": "http://www.linkedin.com/kaw393939"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["linkedin_profile_url"] == updated_data["linkedin_profile_url"]

@pytest.mark.asyncio
async def test_list_users_as_admin(async_client, admin_token):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert 'items' in response.json()

@pytest.mark.asyncio
async def test_list_users_as_manager(async_client, manager_token):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_users_unauthorized(async_client, user_token):
    response = await async_client.get(
        "/users/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403  # Forbidden, as expected for regular user

@pytest.mark.asyncio
@patch('app.utils.minio.getClient')
@patch('app.utils.minio.uploadImage')
@patch('app.dependencies.get_current_user')
@patch('app.dependencies.get_db')
@patch('app.services.user_service.UserService.get_by_email')
@patch('app.services.user_service.UserService.update')
async def test_upload_profile_pic_success(mock_update, mock_get_by_email, mock_get_db, mock_get_current_user, mock_upload_image, mock_get_client, async_client: AsyncClient, user_token):
    mock_get_current_user.return_value = {"user_id": "user@example.com"}
    mock_get_by_email.return_value = MagicMock(id="123")
    mock_get_client.return_value = MagicMock()

    headers = {"Authorization": f"Bearer {user_token}"}
    files = {"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}
    response = await async_client.post("/users/me/upload-profile-picture", headers=headers, files=files)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": "minio:9000/profiles/test_image.jpg"
    }

@pytest.mark.asyncio
@patch('app.dependencies.get_current_user')
@patch('app.dependencies.get_db')
@patch('app.services.user_service.UserService.get_by_email')
async def test_upload_profile_pic_user_not_found(mock_get_by_email, mock_get_db, mock_get_current_user, async_client: AsyncClient, user_token):
    mock_get_current_user.return_value = {"user_id": "nonexistent_user@example.com"}
    mock_get_by_email.return_value = None

    headers = {"Authorization": f"Bearer {user_token}"}
    files = {"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}
    response = await async_client.post("/users/me/upload-profile-picture", headers=headers, files=files)

    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
@patch('app.dependencies.get_current_user')
@patch('app.dependencies.get_db')
@patch('app.services.user_service.UserService.get_by_email')
async def test_upload_profile_pic_invalid_file_type(mock_get_by_email, mock_get_db, mock_get_current_user, async_client: AsyncClient, user_token):
    mock_get_current_user.return_value = {"user_id": "user@example.com"}
    mock_get_by_email.return_value = MagicMock(id="123")

    headers = {"Authorization": f"Bearer {user_token}"}
    files = {"file": ("test_image.gif", b"fake_image_data", "image/gif")}
    response = await async_client.post("/users/me/upload-profile-picture", headers=headers, files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid file type. Only jpeg and png accepted."}

@pytest.mark.asyncio
@patch('app.utils.minio.getClient')
@patch('app.utils.minio.uploadImage')
@patch('app.dependencies.get_current_user')
@patch('app.dependencies.get_db')
@patch('app.services.user_service.UserService.get_by_email')
@patch('app.services.user_service.UserService.update')
async def test_upload_profile_pic_db_update_failure(mock_update, mock_get_by_email, mock_get_db, mock_get_current_user, mock_upload_image, mock_get_client, async_client: AsyncClient, user_token):
    mock_get_current_user.return_value = {"user_id": "user@example.com"}
    mock_get_by_email.return_value = MagicMock(id="123")
    mock_get_client.return_value = MagicMock()
    mock_update.side_effect = Exception("DB update failed")

    headers = {"Authorization": f"Bearer {user_token}"}
    files = {"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}
    response = await async_client.post("/users/me/upload-profile-picture", headers=headers, files=files)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"detail": "DB update failed"}

@pytest.mark.asyncio
@patch('app.utils.minio.getClient')
@patch('app.utils.minio.uploadImage')
@patch('app.dependencies.get_current_user')
@patch('app.dependencies.get_db')
@patch('app.services.user_service.UserService.get_by_email')
@patch('builtins.open', side_effect=Exception("File system error"))
async def test_upload_profile_pic_file_system_error(mock_open, mock_get_by_email, mock_get_db, mock_get_current_user, mock_upload_image, mock_get_client, async_client: AsyncClient, user_token):
    mock_get_current_user.return_value = {"user_id": "user@example.com"}
    mock_get_by_email.return_value = MagicMock(id="123")
    mock_get_client.return_value = MagicMock()

    headers = {"Authorization": f"Bearer {user_token}"}
    files = {"file": ("test_image.jpg", b"fake_image_data", "image/jpeg")}
    
    try:
        # Call the endpoint
        response = await async_client.post("/users/me/upload-profile-picture", headers=headers, files=files)
    except Exception as e:
        # Catch the exception and assert the failure result
        response = e
    
    # Assert the result
    assert isinstance(response, Exception)
    assert str(response) == "File system error"