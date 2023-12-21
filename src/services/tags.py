from typing import List

from sqlalchemy.orm import Session
from src.database.models import Tag
from src.schemas import TagModel


class TagServices:
    def __init__(self, model: Tag):
        self.model = model

    # async def get_tags(skip: int, limit: int, db: Session) -> List[Tag]:
    #     return db.query(Tag).offset(skip).limit(limit).all()


    async def get_tag_by_name(self, db: Session, tag_name: str) -> Tag:
        return db.query(Tag).filter(Tag.name == tag_name).first()
    
    # перевіряє існування тега і створює його при відсутності
    async def create_or_get_tags(self, db: Session, tag_data: list[TagModel]) -> list[Tag]:
        created_tags = []
        for tag_model in tag_data:
            tag = await self.get_tag_by_name(db, tag_model.name)
            if not tag:
                tag = await self.create_tag(db, tag_model)
            created_tags.append(tag)
        return created_tags

    async def create_tag(self, db: Session, tag_model: TagModel) -> Tag:
        tag = Tag(name=tag_model.name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    async def update_tag(self, tag_id: int, tag_model: TagModel, db: Session) -> Tag | None:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag:
            tag.name = tag_model.name
            db.commit()
        return tag

    async def remove_tag(self, tag_id: int, db: Session) -> Tag | None:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if tag:
            db.delete(tag)
            db.commit()
        return tag
