import redis.asyncio as redis
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_limiter.depends import RateLimiter
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import uvicorn
import logging

from src.conf.config import settings
from src.routes import users, comments, auth, tools, static, posts, cloudinary_route

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield



templates = Jinja2Templates(directory="templates")

app = FastAPI(lifespan=lifespan) # type: ignore

app.include_router(users.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(tools.router, prefix="/api")
app.include_router(posts.posts_router, prefix='/posts',
                   dependencies=[Depends(RateLimiter(times=2, seconds=5))])
app.include_router(cloudinary_route.cloud_router, prefix='/cloudinary')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.on_event("startup")
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



@app.get("/", response_class=HTMLResponse, tags=["Main index.html"])
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

# @app.get("/")
# def read_root():
#     """
#     Main function.

#     :return: Message.
#     :rtype: dict
#     """
#     return {"message": "That's root"}




if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=True)
    logging.basicConfig(level=logging.INFO)
