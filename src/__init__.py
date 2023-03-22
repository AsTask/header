from datetime import datetime, timezone

from astask.http.request import RequestMethod
from astask.http.response import HttpResponse, RedirectResponse, ResponseMethod


class Index(RequestMethod, ResponseMethod):
    def __call__(self) -> None:
        name, path = self.__class__.__name__, self.path_info()
        content = f"{name} :: path: {path}"
        self.set_header("test", "test")
        content = f'{content}, has: {self.has_header("test")}'
        content = f'{content}, get: {self.get_header("test")}'
        self.delete_header("test")
        content = f'{content}, delete: has > {self.has_header("test")} get > {self.get_header("test")}.'
        self.set_header("test", "test")
        HttpResponse(content, 200, "text/plain")


class About(ResponseMethod):
    def __call__(self) -> None:
        self.redirect("/redirect")
        # RedirectResponse("/redirect", 308)


class Redirect(RequestMethod, ResponseMethod):
    def __call__(self) -> None:
        dt = datetime.now(timezone.utc)
        dt_year = dt.replace(year=dt.year + 1)
        self.set_cookie("test", "test", expires=dt_year, samesite="lax")
        self.set_cookie("test", "test", expires=dt_year, secure=True)
        self.set_cookie("delete", "delete", expires=dt_year, secure=True, httponly=True, samesite="lax")
        self.delete_cookie("delete")
        self.set_cookie("empty")
        name, path = self.__class__.__name__, self.path_info()
        get, has, error = self.get_cookie("test"), self.has_cookie("test"), self.has_cookie("error")
        self.json_response({"Page": name, 'path': path, "get": get, "has": has, "error": error})
