import typing
from wsgiref.types import WSGIEnvironment

from . import Cookie


class RequestMethod:
    _environ: WSGIEnvironment
    _cookie: Cookie

    def protocol(self) -> str:
        return self._environ["SERVER_PROTOCOL"]

    def user_agent(self) -> str:
        return self._environ["HTTP_USER_AGENT"]

    def scheme(self) -> str:
        return self._environ["wsgi.url_scheme"]

    def host(self) -> str:
        return self._environ["HTTP_HOST"]

    def path_info(self) -> str:
        return self._environ["PATH_INFO"]

    def query_string(self) -> str:
        return self._environ["QUERY_STRING"]

    def request_uri(self) -> str:
        return self._environ["REQUEST_URI"]

    def get_cookie(self, name: str) -> typing.Optional[str]:
        return self._cookie.get(name)

    def has_cookie(self, name: str) -> bool:
        return name in self._cookie
