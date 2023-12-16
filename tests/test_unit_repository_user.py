import asyncio
from datetime import date, datetime, timedelta
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from libgravatar import Gravatar
from pathlib import Path


from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select, text, extract, desc, create_engine



hw_path: str = str(Path(__file__).resolve().parent.parent)
sys.path.append(hw_path)
# print(f"{hw_path=}", sys.path)
os.environ["PYTHONPATH"] += os.pathsep + hw_path
# print(f'{os.environ["PYTHONPATH"]=}')

from src.database.db import get_db
from src.database.models import Base, User
from src.repository import users as repository_users
from src.schemas import UserModel

class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):        
        cls.test_token = "123.456.987"
        DATABASE_URL = "sqlite:///tests/db.sqlite"
        cls.engine = create_engine(DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        cls.session = SessionLocal()
        Base.metadata.drop_all(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)
        cls.testUser = None

        # If want use REAL database can use it:
        # cls.session = next(get_db())

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def get_image(*args, **kwargs):
        return "MOCK IMG"

    # @patch.object(Gravatar, 'get_image', MagicMock(return_value=get_image()))
    @patch('libgravatar.Gravatar.get_image', get_image)
    async def test_add_user(self):
        body=UserModel(
            username="test1",
            email="email@email.com",
            password="pass1235"
        )
        result = await repository_users.create_user(body=body, db=self.session)
        self.testUser = result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, User)
        self.assertEqual(body.username, result.username)
        self.assertEqual(body.email, result.email)
        self.assertEqual(result.confirmed,False, "Just created user must be not confirmed")
        


if __name__ == "__main__":
    unittest.main()
#     # pytest ./tests/unit/
