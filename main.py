import redis.asyncio as redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from src.routes import users, auth
from src.conf.config import settings

app = FastAPI()

app.include_router(users.router, prefix='/api')
app.include_router(auth.router, prefix='/api')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    Startup function.

    :return: None.
    :rtype: None
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)

@app.get("/")
def read_root():
    """
    Main function.

    :return: Message.
    :rtype: dict
    """
    return {"message": "That's root"}