import redis.asyncio as redis
import uvicorn
import logging
from starlette.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi_limiter import FastAPILimiter
from fastapi.templating import Jinja2Templates
from fastapi_limiter.depends import RateLimiter #speed limit

from src.routes.posts import posts_router
from src.routes.cloudinary import cloud_router
from src.conf.config import settings
from src.routes import users, auth, tools, static


templates = Jinja2Templates(directory="templates")
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_router, prefix='/posts',
                   dependencies=[Depends(RateLimiter(times=2, seconds=5))])
app.include_router(cloud_router, prefix='/cloudinary'
                   )
app.include_router(users.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(tools.router, prefix="/api")





@app.on_event("startup")
async def startup():
    """
    Startup function.

    :return: None.
    :rtype: None
    """
    r = await redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)



@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """
    Main HTML index page.
    :return: HTML index page.
    :rtype: 
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "tilte": "Pixel Project"}
    )


static.add_static(app)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000) 