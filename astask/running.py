import typing
from os import getpid
from wsgiref.types import WSGIEnvironment, StartResponse, WSGIApplication

from .http import Http
from .http.logger import Logger
from .http.routing import Call, Routing


class Runner(Http):
    def __init__(self, environ: WSGIEnvironment):
        super().__init__(environ)
        if hasattr(Logger, "level"):
            Logger(environ, self.status_code)


class Running:
    @classmethod
    def route(cls, path: str, call: Call, *args) -> None:
        Routing.routes[path] = call, args

    def __init__(self):
        Routing.routes = dict()

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> WSGIApplication:
        yield Runner(environ)(start_response)

    def run(
            self,
            host: typing.Optional[str] = None,
            port: typing.Optional[int] = None,
            level: typing.Optional[typing.Literal["request", "method", "protocol"]] = None,
    ) -> None:
        try:
            import waitress
            host, port = "127.0.0.1" if host is None else host, 8080 if port is None else port
            if level is not None:
                if (lower := level.lower()) not in ("request", "method", "protocol"):
                    raise ValueError(
                        f"level='{lower}' must be 'request', 'method', 'protocol' or not specified"
                    )
                Logger.level = lower
            print_running(host, port)
            waitress.serve(self, host=host, port=port)
        except ImportError as error:
            print_error(error=error)


def print_running(host: str, port: int) -> None:
    print(f"\033[0;31mINFO:   Started server process [{getpid()}]\033[0m")
    print(f"\033[0;31mINFO:   AsTask running an\033[0m {'http'}://{host}:{port}")


def print_error(error: ImportError) -> None:
    print(f"\n\033[0;31mLibrary '{error.name}' not installed.\033[0m")
