import os
from pathlib import Path
from unittest.mock import MagicMock

hw_path: str = str(Path(__file__).resolve().parent.parent)
os.environ["PATH"] += os.pathsep + hw_path
os.environ["PYTHONPATH"] += os.pathsep + hw_path

from src.database.models import User


def test_create_user(client, user, mock_ratelimiter, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Not confirmed"


def test_login_user(client, user, mock_ratelimiter, session):
    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
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
    assert data["detail"] == "Invalid credentianal"


def test_login_wrong_email(client, user, mock_ratelimiter):
    response = client.post(
        "/api/auth/login",
        data={"username": "email", "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid credentianal"
