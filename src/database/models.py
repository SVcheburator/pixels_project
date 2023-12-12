import enum
from sqlalchemy import Column, Integer, String, Boolean, Table, func, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"  
    user: str = "user" 


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    role = Column("roles", Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)
    active = Column(Boolean, default=False)
    created_at = Column('crated_at', DateTime, default=func.now())


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    owner_id = Column('owner_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    url_original = Column(String(255), nullable=False) 
    url_transformed = Column(String(255), nullable=True)
    url_original_qr = Column(String(255), nullable=False) 
    url_transformed_qr = Column(String(255), nullable=True)
    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")
    description = Column(String(255), nullable=True)
    created_at = Column('crated_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime)
    


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    comment = Column(String(255), nullable=False)
    image_id = Column('image_id', ForeignKey('images.id', ondelete='CASCADE'), default=None)
    owner_id = Column('owner_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    created_at = Column('crated_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True) # Додаємо опцію unique