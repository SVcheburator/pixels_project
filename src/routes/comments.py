from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.orm import Session

# from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.database.models import User
from src.services import auth as auth_service
from src.schemas import CommentBase, CommentResponse
from src.repository import comments as repository_comments
from src.conf import messages


router = APIRouter(prefix="/comments/{image_id}", tags=["Comments by picture"])


@router.get(
    "/",
    response_model=List[CommentResponse],
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    name="Get comments",
)
async def get_comments(
    image_id: int = Path(ge=1),
    limit: int = Query(5, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return await repository_comments.get_comments(image_id, limit, offset, db)


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=60))],
    name="Get comment by id",
)
async def get_comment(
    image_id: int = Path(ge=1),
    comment_id: int = Path(ge=1),
    db: Session = Depends(get_db),
):
    comment = repository_comments.get_comment_by_id(image_id, comment_id, db)

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.COMMENT_NOT_FOUND
        )

    return comment


@router.post(
    "/",
    response_model=CommentResponse,
    # description="No more than 10 requests per minute",
    # dependencies=[Depends(RateLimiter(times=10, seconds=30))],
    name="Create comment",
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    body: CommentBase,
    image_id: int = Path(ge=1),
    owner: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    contact = await repository_comments.create_comment(body, image_id, owner, db)

    return contact
