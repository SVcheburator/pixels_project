import asyncio
from datetime import date, datetime, timedelta
import sys
import os
import unittest
from unittest.mock import MagicMock
from pathlib import Path


from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import select, text, extract, desc, create_engine


hw_path: str = str(Path(__file__).resolve().parent.parent)
sys.path.append(hw_path)
# print(f"{hw_path=}", sys.path)
# os.environ["PYTHONPATH"] += os.pathsep + hw_path
# print(f'{os.environ["PYTHONPATH"]=}')

from src.database.db import get_db
from src.database.models import Bannedlist, Base


from src.repository.logout import add_token, check_token, purge_old


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

        # If want use REAL database can use it:
        # cls.session = next(get_db())

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    async def test_add_token(self):
        result = await add_token(self.test_token, self.session)
        # print(f"{result=}")
        self.assertIsNotNone(result)

    async def test_add_token_wrong_none(self):
        result = await add_token(None, self.session)
        # print(f"{result=}")
        self.assertIsNone(result)

    async def test_add_token_wrong_empty(self):
        result = await add_token("", self.session)
        # print(f"{result=}")
        self.assertIsNone(result)

    async def test_check_token_is(self):
        result = await check_token(self.test_token, self.session)
        # print(f"{result=}")
        self.assertTrue(result)

    async def test_check_token_missed(self):
        result = await check_token("GoIT", self.session)
        # print(f"{result=}")
        self.assertFalse(result)

    async def test_purge_token(self):
        start_range = datetime.now() - timedelta(days=5)
        stmt = select(Bannedlist).where(Bannedlist.token == self.test_token)
        ban = self.session.scalar(stmt)
        ban.created_at = start_range  # type: ignore
        self.session.commit()
        await add_token(self.test_token * 2, self.session)

        result = await purge_old(self.session, duration=1)
        #print(f"{result=}")
        self.assertEqual(result,1)

    async def test_purge_token_empty(self):
        result = await purge_old(self.session, duration=1)
        #print(f"{result=}")
        self.assertEqual(result,0)


if __name__ == "__main__":
    unittest.main()
