from abc import ABC, abstractmethod
from flask import request
from app.utils.util import parse_json


class CmnController(ABC):
    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_TEXT = "text/plain"

    RESPONSE_HEADERS = {
        "Cache-Control": "no-store",
        "Content-Type": "application/json; charset=UTF-8",
        "Connection": "close",
        "Expires": "-1",
        "Pragma": "no-cache",
        "X-Frame-Options": "SAMEORIGIN",
        "Content-Security-Policy": "reflected-xss block",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block"
    }

    request_params = dict()
    request_addition = dict()

    form = None

    def __init__(self, *args, **kwargs):
        if 'request_addition' in kwargs:
            self.request_addition = kwargs['request_addition']

    def main(self):
        self.request_params = self.get_request()

        return self.execute()

    @abstractmethod
    def execute(self):
        pass

    def get_request(self) -> dict:
        request_url = request.args.to_dict()

        if len(self.request_addition) > 0 and isinstance(self.request_addition, dict):
            request_url.update(self.request_addition)

        request_body = self.get_body_request()

        return request_body | request_url

    def get_body_request(self) -> dict:
        request_body = dict()
        if len(request.data) == 0:
            return request_body

        if request.content_type and (request.content_type.startswith(self.CONTENT_TYPE_JSON) or request.content_type.startswith(self.CONTENT_TYPE_TEXT)):
            request_body = parse_json(request.data)

        return request_body
