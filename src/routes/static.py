import pathlib

from fastapi import Response
from fastapi.staticfiles import StaticFiles

from src.conf.config import settings


class StaticFilesCache(StaticFiles):
    def __init__(
        self,
        *args,
        cachecontrol="public, max-age=31536000, s-maxage=31536000, immutable",
        **kwargs
    ):
        self.cachecontrol = cachecontrol
        super().__init__(*args, **kwargs)

    def file_response(self, *args, **kwargs) -> Response:
        resp: Response = super().file_response(*args, **kwargs)
        resp.headers.setdefault("Cache-Control", self.cachecontrol)
        return resp


def add_static(_app):
    _app.mount(
        path="/static",
        app=StaticFilesCache(
            directory=settings.STATIC_DIRECTORY, cachecontrol="private, max-age=3600"
        ),
        name="static",
    )
    _app.mount(
        path="/sphinx",
        app=StaticFilesCache(directory=settings.SPHINX_DIRECTORY, html=True),
        name="sphinx",
    )


static_dir: pathlib.Path = pathlib.Path(settings.STATIC_DIRECTORY)