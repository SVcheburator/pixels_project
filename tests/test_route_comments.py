from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User, Comment, Image, Role
from src.services.auth import auth_service
from src.conf import messages


@pytest.fixture()
def user_admin(client, user, mock_ratelimiter, session, monkeypatch):
    mock_send_email = MagicMock()
    get_image = MagicMock(return_value="MOC_AVATAR")
    add_task = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    monkeypatch.setattr("libgravatar.Gravatar.get_image", get_image)
    monkeypatch.setattr("fastapi.BackgroundTasks.add_task", add_task)

    client.post("/api/auth/signup", json=user)

    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    current_user.active = True

    session.commit()

    return current_user


@pytest.fixture()
def user_simple(client, next_user, mock_ratelimiter, session, monkeypatch):
    mock_send_email = MagicMock()
    get_image = MagicMock(return_value="MOC_AVATAR")
    add_task = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    monkeypatch.setattr("libgravatar.Gravatar.get_image", get_image)
    monkeypatch.setattr("fastapi.BackgroundTasks.add_task", add_task)

    client.post("/api/auth/signup", json=next_user)

    current_user: User = (
        session.query(User).filter(User.email == next_user.get("email")).first()
    )
    current_user.confirmed = True
    current_user.active = True

    session.commit()

    return current_user


@pytest.fixture()
def user_moderator(client, next_user_moderator, mock_ratelimiter, session, monkeypatch):
    mock_send_email = MagicMock()
    get_image = MagicMock(return_value="MOC_AVATAR")
    add_task = MagicMock()
    monkeypatch.setattr("src.services.emails.send_email", mock_send_email)
    monkeypatch.setattr("libgravatar.Gravatar.get_image", get_image)
    monkeypatch.setattr("fastapi.BackgroundTasks.add_task", add_task)

    client.post("/api/auth/signup", json=next_user_moderator)

    current_user: User = (
        session.query(User)
        .filter(User.email == next_user_moderator.get("email"))
        .first()
    )
    current_user.confirmed = True
    current_user.active = True
    current_user.role = Role.moderator

    session.commit()

    return current_user


@pytest.fixture()
def token_admin(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture()
def token_user(client, next_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": next_user.get("email"),
            "password": next_user.get("password"),
        },
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture()
def token_moderator(client, next_user_moderator):
    response = client.post(
        "/api/auth/login",
        data={
            "username": next_user_moderator.get("email"),
            "password": next_user_moderator.get("password"),
        },
    )
    data = response.json()
    return data["access_token"]


def test_create_comment_by_admin(client, user_admin, token_admin, session):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        # create image
        image = Image(
            owner=user_admin, url_original="some_url", url_original_qr="some_url"
        )
        session.add(image)
        session.commit()
        session.refresh(image)

        # comment response
        response = client.post(
            f"/api/comments/{image.id}/",
            json={"comment": "test comment"},
            headers={"Authorization": f"Bearer {token_admin}"},
        )

        # tests
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["comment"] == "test comment"
        assert "id" in data


def test_create_comment_by_user(client, user_simple, token_user, session):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        # create image
        image = Image(
            owner=user_simple, url_original="some_url", url_original_qr="some_url"
        )
        session.add(image)
        session.commit()
        session.refresh(image)

        # comment response
        response = client.post(
            f"/api/comments/{image.id}/",
            json={"comment": "test comment"},
            headers={"Authorization": f"Bearer {token_user}"},
        )

        # tests
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["comment"] == "test comment"
        assert "id" in data


def test_create_comment_by_moderator(client, user_moderator, token_moderator, session):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        # create image
        image = Image(
            owner=user_moderator, url_original="some_url", url_original_qr="some_url"
        )
        session.add(image)
        session.commit()
        session.refresh(image)

        # comment response
        response = client.post(
            f"/api/comments/{image.id}/",
            json={"comment": "test comment"},
            headers={"Authorization": f"Bearer {token_moderator}"},
        )

        # tests
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["comment"] == "test comment"
        assert "id" in data


def test_create_comment_by_admin_image_not_found(client, user_admin, token_admin):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        image_id = 10

        # comment response
        response = client.post(
            f"/api/comments/{image_id}/",
            json={"comment": "test comment"},
            headers={"Authorization": f"Bearer {token_admin}"},
        )

        # tests
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.IMAGE_NOT_FOUND


def test_create_comment_by_user_image_not_found(client, user_admin, token_admin):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        image_id = 10

        # comment response
        response = client.post(
            f"/api/comments/{image_id}/",
            json={"comment": "test comment"},
            headers={"Authorization": f"Bearer {token_admin}"},
        )

        # tests
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.IMAGE_NOT_FOUND


def test_create_comment_by_moderator_image_not_found(
    client, user_moderator, token_admin
):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        image_id = 10

        # comment response
        response = client.post(
            f"/api/comments/{image_id}/",
            json={"comment": "test comment"},
            headers={"Authorization": f"Bearer {token_admin}"},
        )

        # tests
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.IMAGE_NOT_FOUND
