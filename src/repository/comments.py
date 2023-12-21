from typing import List

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from src.database.models import Comment, User, Image
from src.schemas import CommentBase


async def get_comments(
    image_id: int, limit: int, offset: int, db: Session
) -> List[Comment]:
    """
    The get_comments function returns a list of comments for the image with the given id.
    The limit and offset parameters are used to paginate through results.

    :param image_id: int: Filter the comments by image_id
    :param limit: int: Limit the number of comments returned
    :param offset: int: Specify the number of comments to skip before returning the results
    :param db: Session: Pass the database session to the function
    :return: A list of comment objects
    """
    return (
        db.query(Comment)
        .filter(Comment.image_id == image_id)
        .limit(limit)
        .offset(offset)
        .all()
    )


async def get_comment_by_id(
    image_id: int, comment_id: int, db: Session
) -> Comment | None:
    """
    The get_comment_by_id function returns a comment by its id.

    :param image_id: int: Filter the comments by image_id
    :param comment_id: int: Filter the comments by their id
    :param db: Session: Pass the database session to the function
    :return: A comment object or none
    """
    return (
        db.query(Comment)
        .filter(Comment.image_id == image_id, Comment.id == comment_id)
        .first()
    )


async def create_comment(
    body: CommentBase, image_id: int, owner: User, db: Session
) -> Comment | None:
    """
    The create_comment function creates a new comment for an image.

    :param body: CommentBase: Pass in the comment object from the request body
    :param image_id: int: Get the image id from the database
    :param owner: User: Get the user that is making the comment
    :param db: Session: Pass in the database session
    :return: A comment object
    """
    try:
        comment = Comment(owner=owner, image_id=image_id, comment=body.comment)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    except Exception as err:
        print(f"create_comment {err=}")


async def update_comment(
    image_id: int, comment_id: int, body: CommentBase, owner: User, db: Session
) -> Comment | None:
    """
    The update_comment function updates a comment in the database.

    :param image_id: int: Identify the image that the comment belongs to
    :param comment_id: int: Filter the comment that is being updated
    :param body: CommentBase: Pass the new comment to the function
    :param owner: User: Check if the user is the owner of the comment
    :param db: Session: Access the database
    :return: A comment object or none
    """
    comment = (
        db.query(Comment)
        .filter(
            and_(
                Comment.image_id == image_id,
                Comment.id == comment_id,
                Comment.owner_id == owner.id,
            )
        )
        .first()
    )

    if comment:
        comment.comment = body.comment
        db.commit()

    return comment


async def remove_comment(
    image_id: int, comment_id: int, owner: User, db: Session
) -> Comment | None:
    """
    The remove_comment function removes a comment from the database.

    :param image_id: int: Find the image that the comment is on
    :param comment_id: int: Identify the comment to be removed
    :param owner: User: Check if the user is the owner of the comment
    :param db: Session: Access the database
    :return: A comment object or none
    """
    comment = (
        db.query(Comment)
        .filter(
            and_(
                Comment.image_id == image_id,
                Comment.id == comment_id,
                Comment.owner_id == owner.id,
            )
        )
        .first()
    )

    if comment:
        db.delete(comment)
        db.commit()

    return comment


async def get_image_by_id(image_id: int, db: Session):
    """
    The get_image_by_id function returns an image object from the database, given its id.


    :param image_id: int: Specify the id of the image that is being requested
    :param db: Session: Pass the database session to the function
    :return: A single image object from the database
    """
    return db.query(Image).filter(Image.id == image_id).first()
