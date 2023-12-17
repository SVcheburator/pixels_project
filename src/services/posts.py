# pixels_project\src\services\posts.py
from typing import List, Any
from sqlalchemy.orm import Session
from src.services.core import BaseServices, ModelType
from src.database.models import Image
from src.schemas import PostCreate, PostUpdate



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
        
        new_post_data = PostCreate(
            text=post_data.text,
            user=post_data.user,
            url_original=post_data.url_original,
            img=file_path,
        )

        post = await self.create(db, obj_in=new_post_data)
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


    def post_list_by_user(self, db: Session, user_id: int) -> List[Image]:
        """
        Отримання списку світлин за ID користувача
        """
        return db.query(self.model).filter(self.model.owner_id == user_id).all()


    def get_p_by_unique_identifier(self, db: Session, unique_identifier: str) -> Any:
            return db.query(Image).filter(Image.url_original_qr == unique_identifier).first()



    async def get_post_by_url_original(
        self,
        db: Session,
        url_original: str,
    ) -> ModelType:
        """
        Отримання запису за url_original
        """
        return db.query(self.model).filter_by(url_original=url_original).first()
    


    @staticmethod
    async def get_post_url(db: Session, url_original: str) -> Image:
        """
        Отримання запису за url_original
        """
        return db.query(Image).filter(Image.url_original == url_original).first()




    @staticmethod
    async def get_post_by_description(db: Session, description: str) -> Image:
        """
        Отримання запису за параметром бази даних (description)
        """
        return db.query(Image).filter(Image.description == description).first()



post = PostServices(Image)

