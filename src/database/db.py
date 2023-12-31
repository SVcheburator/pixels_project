from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.conf.config import settings

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
# print(f"db.py {SQLALCHEMY_DATABASE_URL=}")
# assert SQLALCHEMY_DATABASE_URL, "SQLALCHEMY_DATABASE_URL MUST BE IN .env" 
engine = None
if SQLALCHEMY_DATABASE_URL: 
    engine = create_engine(SQLALCHEMY_DATABASE_URL) # echo=True

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()