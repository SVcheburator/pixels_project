import os
from pathlib import Path
from unittest.mock import MagicMock

hw_path: str = str(Path(__file__).resolve().parent.parent)
os.environ["PATH"] += os.pathsep + hw_path
# os.environ["PYTHONPATH"] += os.pathsep + hw_path

from src.conf import messages
from src.database.models import User, Role
from src.services.auth import auth_service


def test_create_admin_user(client, user, mock_ratelimiter, monkeypatch):
    mock_send_email = MagicMock()
    get_image = MagicMock(return_value="MOC_AVATAR")
    add_task = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    monkeypatch.setattr("libgravatar.Gravatar.get_image", get_image)
    monkeypatch.setattr("fastapi.BackgroundTasks.add_task", add_task)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    # print(data)
    assert data["user"]["email"] == user.get("email")
    assert data["detail"] == messages.AUTH_USER_CREATED_CONFIRM
    assert data["user"]["role"] == 'admin'
    assert "id" in data["user"]


def test_repeat_create_same_user(client, user, mock_ratelimiter, monkeypatch):
    mock_send_email = MagicMock()
    get_image = MagicMock(return_value="MOC_AVATAR")
    add_task = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    monkeypatch.setattr("libgravatar.Gravatar.get_image", get_image)
    monkeypatch.setattr("fastapi.BackgroundTasks.add_task", add_task)

    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == messages.AUTH_ALREADY_EXIST

def test_create_general_user(client, next_user, mock_ratelimiter, monkeypatch):
    mock_send_email = MagicMock()
    get_image = MagicMock(return_value="MOC_AVATAR")
    add_task = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    monkeypatch.setattr("libgravatar.Gravatar.get_image", get_image)
    monkeypatch.setattr("fastapi.BackgroundTasks.add_task", add_task)
    response = client.post(
        "/api/auth/signup",
        json=next_user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    # print(data)
    assert data["user"]["email"] == next_user.get("email")
    assert data["detail"] == messages.AUTH_USER_CREATED_CONFIRM
    assert data["user"]["role"] == next_user.get("role")
    assert "id" in data["user"]


def test_login_user_not_confirmed(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.AUTH_EMAIL_NOT_CONF


def test_login_user_not_active(client, user, mock_ratelimiter, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True # type: ignore
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.AUTH_EMAIL_NOT_ACTIVE


def test_login_user(client, user, mock_ratelimiter, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True # type: ignore
    current_user.active = True # type: ignore
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.AUTH_INVALID_PASSW


def test_login_wrong_email(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": "email", "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == messages.AUTH_EMAIL_INVALID


def test_refresh_token_user(client, user, mock_ratelimiter, session):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

    token = data["refresh_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/auth/refresh_token",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    assert data["refresh_token"] == current_user.refresh_token

def test_delete_general_user(client, user, next_user, mock_ratelimiter, monkeypatch, session):
    # Admin login
    response_admin = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response_admin.status_code == 200, response_admin.text
    data = response_admin.json()
    assert data["token_type"] == "bearer"
    token = data["access_token"]

    # find ID og general user for delete
    general_user: User = session.query(User).filter(User.email == next_user.get("email")).first()
    user_id = general_user.id
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(
        f"/api/users/{user_id}",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["detail"] == messages.USER_ACCEPDED


def test_confirm_general_user(client, next_user, mock_ratelimiter, monkeypatch, session):
    test_create_general_user(client, next_user, mock_ratelimiter, monkeypatch)

    token = auth_service.create_email_token({"sub": next_user.get("email")})
    # print(f"{token=}")
    response = client.get(
        f"/api/auth/confirmed_email/{token}",
    )
    assert response.status_code == 200, response.text
    data = response.json()
    # print(data)
    assert data["message"] == messages.AUTH_EMAIL_CONF

    new_user: User = session.query(User).filter(User.email == next_user.get("email")).first()
    assert new_user is not None
    assert new_user.confirmed == True  # type: ignore
    assert new_user.active == True # type: ignore

