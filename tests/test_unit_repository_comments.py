import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta


from sqlalchemy.orm import Session


from src.database.models import Comment, User
from src.schemas import CommentBase
from src.repository.comments import (
    get_comments,
    get_comment_by_id,
    create_comment,
    update_comment,
    remove_comment,
)


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        """
        The setUp function is called before each test function.
        It creates a mock session object, a user object, and two comment objects.

        :param self: Represent the instance of the class
        :return: None
        """
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@test.com")
        self.body = CommentBase(comment="some comment")
        self.image_id = 1
        self.comment_id = 1

    async def test_get_comments(self) -> None:
        """
        The test_get_comments function tests the get_comments function.
        It does this by mocking out the session object and returning a list of comments.
        The test then asserts that the result is equal to what was returned from get_comments.

        :param self: Represent the instance of the class
        :return: None
        """
        comments = [Comment(), Comment(), Comment()]

        self.session.query().filter().limit().offset().all.return_value = comments
        result = await get_comments(self.image_id, 10, 0, self.session)
        self.assertEqual(result, comments)

    async def test_get_comment_by_id(self) -> None:
        """
        The test_get_comment_by_id function tests the get_comment_by_id function.
            It does this by mocking out the session object and returning a comment object.
            The test then asserts that the result of calling get_comment_by_id is equal to
            our mocked comment.

        :param self: Access the attributes and methods of the class in python
        :return: None
        """
        comment = Comment()

        self.session.query().filter().first.return_value = comment
        result = await get_comment_by_id(self.image_id, self.comment_id, self.session)
        self.assertEqual(result, comment)

    async def test_create_comment(self) -> None:
        """
        The test_create_comment function tests the create_comment function.
            It creates a comment and checks that it has been created correctly.

        :param self: Represent the instance of the class
        :return: None
        """
        result = await create_comment(self.body, self.image_id, self.user, self.session)
        self.assertEqual(result.comment, self.body.comment)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_comment_found(self) -> None:
        """
        The test_update_comment_found function tests the update_comment
        function when a comment is found.

        :param self: Represent the instance of a class
        :return: None
        """
        comment = Comment()
        self.session.query().filter().first.return_value = comment
        self.session.commit.return_value = None
        result = await update_comment(
            self.image_id, self.comment_id, self.body, self.user, self.session
        )
        self.assertEqual(result, comment)

    async def test_update_comment_not_found(self) -> None:
        """
        The test_update_comment_not_found function tests the update_comment
        function when a comment is not found.

        :param self: Represent the instance of a class
        :return: None
        """
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_comment(
            self.image_id, self.comment_id, self.body, self.user, self.session
        )
        self.assertIsNone(result)

    async def test_delete_comment_found(self) -> None:
        """
        The test_delete_comment_found function tests the remove_comment
        function when a comment is found.

        :param self: Represent the instance of a class
        :return: None
        """
        comment = Comment()
        self.session.query().filter().first.return_value = comment
        self.session.commit.return_value = None
        result = await remove_comment(
            self.image_id, self.comment_id, self.user, self.session
        )
        self.assertEqual(result, comment)

    async def test_delete_comment_not_found(self) -> None:
        """
        The test_delete_comment_not_found function tests the remove_comment
        function when a comment is not found.

        :param self: Represent the instance of a class
        :return: None
        """
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await remove_comment(
            self.image_id, self.comment_id, self.user, self.session
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
