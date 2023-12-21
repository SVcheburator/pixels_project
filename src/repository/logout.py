from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from datetime import date, timedelta

from src.database.models import Bannedlist


async def add_token(token: str|None, db: Session) -> int | None:
    """Add token to black list 

    :param token: auth_token
    :type token: str | None
    :param db: Database session connection
    :type db: Session
    :return: id of added token
    :rtype: int | None
    """
    if token:
        try:
            obj = Bannedlist(token=token)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj.id # type: ignore
        except Exception as err:
            print(f"DB error {err=}")
            return None


async def check_token(token: str, db: Session) -> bool:
    """Chack token present on database or no

    :param token: auth_token
    :type token: str
    :param db: Database session connection
    :type db: Session
    :return: True if token is present on database
    :rtype: bool
    """
    stmt = select(Bannedlist.id).where(Bannedlist.token==token)
    result = db.scalar(stmt)
    # print(f"{result=}")
    # result = db.query(Bannedlist).filter_by(token=token).first()
    return result is not None


async def purge_old(db: Session, duration: int = 7) -> int:
    """_summary_

    :param db: Purge old records for expired tokens
    :type db: Session
    :param duration: Day how old token will be purged, defaults to 7
    :type duration: int, optional
    :return: How many recods was deleted
    :rtype: int
    """
    start_range = date.today() + timedelta(days=-duration)
    stmt = delete(Bannedlist).where(Bannedlist.created_at <= start_range)
    result = db.execute(stmt)
    db.commit()
    return result.rowcount



