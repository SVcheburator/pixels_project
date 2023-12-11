# pixels_project\src\services\posts.py
from sqlalchemy.orm import Session

from src.services.core import BaseServices, ModelType
from src.database.models import Comment, Image
from src.schemas import CommentCreate, CommentUpdate, PostCreate, PostUpdate

class PostServices(BaseServices[Image, PostCreate, PostUpdate]):
    """
    Дії з постом
    """

    async def post_list_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[ModelType]:
        return db.query(self.model).filter(self.model.user == user_id).all()

post = PostServices(Image)

class CommentServices(BaseServices[Comment, CommentCreate, CommentUpdate]):
    """
    Дії з коментарями
    """

    async def comments_by_post(
        self,
        db: Session,
        post_id: int,
    ) -> list[ModelType]:
        """
        Список коментаріїв
        """
        return db.query(self.model).filter(self.model.post == post_id).all()

comment = CommentServices(Comment)