from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import logging
from fastapi_limiter.depends import RateLimiter #speed limit

from src.routes.posts import posts_router
from src.routes.cloudinary import cloud_router

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000) 