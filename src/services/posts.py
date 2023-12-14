# pixels_project\src\services\posts.py

from sqlalchemy.orm import Session
from src.services.core import BaseServices, ModelType
from src.database.models import Comment, Image
from src.schemas import CommentCreate, CommentUpdate, PostCreate, PostUpdate


class PostServices(BaseServices[Image, PostCreate, PostUpdate]):
    """
    Дії з постом
    """
    def __init__(self, model: Image):
        self.model = model

    async def create_post(
        self,
        db: Session,
        post_data: PostCreate,
        file_path: str,
    ) -> ModelType:
        """
        Створення нового посту і збереження URL зображення в базі даних
        """
        # Збереження URL зображення в об'єкті PostCreate
        post_data.url_original = file_path

        # Викликайте метод create базового класу, передаючи відповідні дані
        post = await super().create(db, obj_in=post_data)
        return post



    async def update_post_image_url(
        self,
        db: Session,
        post_id: int,
        url: str,
    ) -> ModelType:
        """
        Оновлення URL зображення в пості
        """
        post = await self.get_p(db, id=post_id)
        if post:
            post.url_original = url
            db.commit()
            db.refresh(post)
        return post


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
