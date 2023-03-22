from wsgiref.types import WSGIEnvironment

from . import response_status


class Logger:
    level: str

    def __init__(self, environ: WSGIEnvironment, status_code: int) -> None:
        self.environ = environ
        request = self.request(status_code)
        if "method" == self.level:
            request = self.method(request)
        elif "protocol" == self.level:
            request = self.protocol(request)
        print(f"INFO:   {self.environ['REMOTE_ADDR']}:{self.environ['REMOTE_PORT']}   {request}")

    def request(self, status_code: int) -> str:
        request = f"{self.environ['REQUEST_URI']} : {response_status(status_code)}"
        if 400 <= status_code:
            return f"\033[0;31m{request}\033[0m"
        if 300 <= status_code:
            return f"\033[0;36m{request}\033[0m"
        return request

    def method(self, request: str) -> str:
        method = self.environ["REQUEST_METHOD"]
        return f"{method:5s}{request}"

    def protocol(self, request: str) -> str:
        protocol = self.environ["SERVER_PROTOCOL"]
        method = self.environ["REQUEST_METHOD"]
        return f"{protocol} : {method:5s}{request}"
