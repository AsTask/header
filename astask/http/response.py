import json
import time
import typing
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from http.cookies import BaseCookie
from wsgiref.types import WSGIEnvironment

from . import Http

_environ: WSGIEnvironment


def _charset(media_type: str, charset: str) -> str:
    return f"{media_type}; charset={charset}"


def _redirect(code: int) -> int:
    if "HTTP/1.0" == _environ["SERVER_PROTOCOL"]:
        return 302 if 307 == code else 301
    return code


class HttpResponse:
    _http: Http

    def __init__(
            self,
            content: typing.Union[bytes, str],
            status_code: int,
            media_type: str,
            charset: typing.Optional[str] = None,
    ) -> None:
        self._http.status_code = status_code
        current_charset = "utf-8" if charset is None else charset
        if media_type.startswith("text/"):
            self._http.media_type = _charset(media_type, current_charset)
        else:
            self._http.media_type = media_type
        self._http.body = content.encode(current_charset) if isinstance(content, str) else content


class PlainResponse(HttpResponse):
    def __init__(self, text: str, status_code: int = 200, charset: typing.Optional[str] = None) -> None:
        HttpResponse.__init__(self, text, status_code, "text/plain", charset)


class HtmlResponse(HttpResponse):
    def __init__(self, html: str, status_code: int = 200, charset: typing.Optional[str] = None) -> None:
        HttpResponse.__init__(self, html, status_code, "text/html", charset)


class JsonResponse(HttpResponse):
    def __init__(self, data: typing.Any, status_code: int = 200) -> None:
        HttpResponse.__init__(self, json.dumps(data), status_code, "application/json")


class RedirectResponse:
    _http: Http

    def __init__(self, url: str, status_code: typing.Literal[307, 308] = 307) -> None:
        if status_code not in (307, 308):
            raise ValueError(
                f"status_code={status_code}, for a redirect it can be 307 or 308"
            )
        self._http.header["location"] = url
        self._http.status_code = _redirect(status_code)
        self._http.media_type = "text/plain"
        self._http.body = b""


class ResponseMethod:
    _http: Http

    def set_header(self, name: str, value: str) -> None:
        self._http.header[name.lower()] = value

    def delete_header(self, name: str) -> None:
        if (lower := name.lower()) in self._http.header:
            del self._http.header[lower]

    def has_header(self, name: str) -> bool:
        return name.lower() in self._http.header

    def get_header(self, name: str) -> typing.Optional[str]:
        return self._http.header.get(name.lower())

    def set_cookie(
            self,
            key: str,
            value: str = "",
            expires: typing.Optional[typing.Union[datetime, str, int]] = None,
            max_age: typing.Optional[typing.Union[timedelta, int]] = None,
            path: str = "/",
            domain: typing.Optional[str] = None,
            secure: bool = False,
            httponly: bool = False,
            samesite: typing.Optional[typing.Literal["lax", "strict", "none"]] = None,
    ) -> None:
        cookie = BaseCookie()
        cookie[key] = value
        if expires is not None:
            if isinstance(expires, datetime):
                cookie[key]["expires"] = format_datetime(expires, usegmt=True)
            else:
                cookie[key]["expires"] = expires
        if max_age is not None:
            if isinstance(max_age, timedelta):
                max_age = max_age.total_seconds()
            cookie[key]["max-age"] = int(max_age)
            if not expires:
                cookie[key]["expires"] = format_datetime(
                    datetime.fromtimestamp(time.time() + max_age, timezone.utc), usegmt=True
                )
        if path is not None:
            cookie[key]["path"] = path
        if domain is not None:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            if samesite.lower() not in ("lax", "none", "strict"):
                raise ValueError(
                    f"samesite='{samesite}' must be 'lax', 'none', or 'strict'."
                )
            cookie[key]["samesite"] = samesite
        self._http.cookie[key] = cookie[key].output(header="").strip()

    def delete_cookie(self, key: str, path: str = "/", domain: typing.Optional[str] = None) -> None:
        self.set_cookie(key, "", "Thu, 01 Jan 1970 00:00:00 GMT", 0, path, domain)

    def response(
            self,
            content: typing.Union[bytes, str],
            status_code: int,
            media_type: str,
            charset: typing.Optional[str] = None,
    ) -> None:
        self._http.status_code = status_code
        current_charset = "utf-8" if charset is None else charset
        if media_type.startswith("text/"):
            self._http.media_type = _charset(media_type, current_charset)
        else:
            self._http.media_type = media_type
        self._http.body = content.encode(current_charset) if isinstance(content, str) else content

    def plain_response(self, text: str, status_code: int = 200, charset: typing.Optional[str] = None) -> None:
        self.response(text, status_code, "text/plain", charset)

    def html_response(self, html: str, status_code: int = 200, charset: typing.Optional[str] = None) -> None:
        self.response(html, status_code, "text/html", charset)

    def json_response(self, data: typing.Any, status_code: int = 200) -> None:
        self.response(json.dumps(data), status_code, "application/json")

    def redirect(self, url: str, status_code: typing.Literal[307, 308] = 307) -> None:
        if status_code not in (307, 308):
            raise ValueError(
                f"status_code={status_code}, for a redirect it can be 307 or 308"
            )
        self._http.header["location"] = url
        self._http.status_code = _redirect(status_code)
        self._http.media_type = "text/plain"
        self._http.body = b""
