import typing
from collections.abc import Callable

from .response import HttpResponse


class Error:
    def __init__(self, status_code: int) -> None:
        HttpResponse(b"Not Found", status_code, "text/plain")


Call: typing.TypeAlias = Callable[..., Callable[..., None]]


class Routing:
    routes: typing.Dict[str, typing.Tuple[Call, typing.Tuple]]

    def __init__(self, path: str) -> None:
        if path in self.routes:
            call, args = self.routes[path]
            call(*args)()
        else:
            Error(404)
