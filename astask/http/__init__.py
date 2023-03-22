import typing
from importlib import import_module
from types import ModuleType
from wsgiref.types import WSGIEnvironment, StartResponse


def response_status(status_code: int) -> str:
    return {
        200: "200 OK",
        301: "301 Moved Permanently",
        302: "302 Moved Temporarily",
        307: "307 Temporary Redirect",
        308: "308 Permanent Redirect",
        404: "404 Not Found",
        500: "500 Internal Server Error",
    }.get(status_code, "520 Unknown Error")


class Headers:
    header: typing.Dict[str, str]
    cookie: typing.Dict[str, str]


class Http(Headers):
    def __init__(self, environ: WSGIEnvironment) -> None:
        self.header = dict()
        self.cookie = dict()
        self.status_code = 200
        self.media_type = "text/plain; charset=utf-8"
        self.body = b"Default Page"
        package = import_module(__package__)
        module_attribute(package, environ, self)
        package.routing.Routing(environ["PATH_INFO"])

    def __call__(self, start_response: StartResponse) -> bytes:
        for key, _ in (headers := [
            ("content-length", str(len(self.body))), ("content-type", self.media_type)
        ]):
            if key in self.header:
                del self.header[key]
        if self.header:
            headers.extend([(key, value) for key, value in self.header.items()])
        if self.cookie:
            headers.extend([("set-cookie", value) for _, value in self.cookie.items()])
        start_response(response_status(self.status_code), headers)
        return self.body


class Cookie(dict):
    def __init__(self, environ: WSGIEnvironment) -> None:
        dict.__init__(self)
        if "HTTP_COOKIE" in environ:
            for cookie in [cookie for cookie in environ["HTTP_COOKIE"].split("; ")]:
                key, value = cookie.split("=")
                self[key] = value


def module_attribute(package: ModuleType, environ: WSGIEnvironment, http: Http) -> None:
    for attr, value in (("_environ", environ), ("_cookie", Cookie(environ))):
        setattr(package.request.RequestMethod, attr, value)
    setattr(package.response, "_environ", environ)
    for attribute in ("HttpResponse", "RedirectResponse", "ResponseMethod"):
        setattr(getattr(package.response, attribute), "_http", http)
