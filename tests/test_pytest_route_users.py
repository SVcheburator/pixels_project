import os
from pathlib import Path
from unittest.mock import MagicMock

hw_path: str = str(Path(__file__).resolve().parent.parent)
os.environ["PATH"] += os.pathsep + hw_path
os.environ["PYTHONPATH"] += os.pathsep + hw_path

from src.conf import messages
from src.database.models import User, Role


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

def test_create_general_user(client, user, mock_ratelimiter, monkeypatch):
    mock_send_email = MagicMock()
    get_image = MagicMock(return_value="MOC_AVATAR")
    add_task = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    monkeypatch.setattr("libgravatar.Gravatar.get_image", get_image)
    monkeypatch.setattr("fastapi.BackgroundTasks.add_task", add_task)
    user_next = user.copy()
    user_next["username"]  = "nextuser"
    user_next["email"]  = "nextuser@example.com"
    response = client.post(
        "/api/auth/signup",
        json=user_next,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    # print(data)
    assert data["user"]["email"] == user_next.get("email")
    assert data["detail"] == messages.AUTH_USER_CREATED_CONFIRM
    assert data["user"]["role"] == user_next.get("role")
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




# def test_login_wrong_password(client, user, mock_ratelimiter):
#     response = client.post(
#         "/api/auth/login",
#         data={"username": user.get("email"), "password": "password"},
#     )
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == "Invalid credentianal"


# def test_login_wrong_email(client, user, mock_ratelimiter):
#     response = client.post(
#         "/api/auth/login",
#         data={"username": "email", "password": user.get("password")},
#     )
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == "Invalid credentianal"
