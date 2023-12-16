from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from src.services.cloudinary import CloudinaryService

cloud_router = APIRouter(prefix='/cloudinary')

# Отримання трансформованого зображення
@cloud_router.get("/get_transformed_image/{image_id}")
async def get_transformed_image(image_id: str):
    # Задайте параметри трансформації, наприклад, розмір, обрізка і т.д.
    transformation_params = {
        'width': 300,
        'height': 300,
        'crop': 'fill',
    }

    # Створення посилання на трансформоване зображення
    try:
        transformed_url = await CloudinaryService.upload_and_transform_image_async(image_id, transformation_params)

        # Можете вивести результат у вигляді HTML-сторінки або іншого формату відповіді
        html_content = f"<img src='{transformed_url}' alt='Transformed Image'>"
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

