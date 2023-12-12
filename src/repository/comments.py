from typing import List

# from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from src.database.models import Comment, User
from src.schemas import CommentBase


async def get_comments(
    image_id: int, limit: int, offset: int, db: Session
) -> List[Comment]:
    return (
        db.query(Comment)
        .filter(Comment.image_id == image_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


def get_comment_by_id(image_id: int, comment_id: int, db: Session) -> Comment | None:
    return (
        db.query(Comment)
        .filter(Comment.image_id == image_id, Comment.id == comment_id)
        .first()
    )


async def create_comment(
    body: CommentBase, image_id: int, owner: User, db: Session
) -> Comment:
    comment = Comment(owner=owner, image_id=image_id, comment=body.comment)

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment
