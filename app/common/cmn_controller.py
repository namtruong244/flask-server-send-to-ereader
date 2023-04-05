from abc import ABC, abstractmethod
from flask import request, make_response, jsonify, g, Response

from .cmn_logger import CmnLogger
from app.common import NotFoundConfigException
from app.utils.util import parse_json


class CmnController(ABC):
    CODE_SUCCESS = '00000'
    CODE_SUCCESS_CREATE = '00001'

    CONTENT_TYPE_JSON = 'application/json'
    CONTENT_TYPE_TEXT = 'text/plain'

    RESPONSE_HEADERS = (
        ('Cache-Control', 'no-store'),
        ('Content-Type', 'application/json; charset=UTF-8'),
        ('Connection', 'close'),
        ('Expires', '-1'),
        ('Pragma', 'no-cache'),
        ('X-Frame-Options', 'SAMEORIGIN'),
        ('Content-Security-Policy', 'reflected-xss block'),
        ('X-Content-Type-Options', 'nosniff'),
        ('X-XSS-Protection', '1; mode=bloc')
    )

    request_params = dict()
    request_addition = dict()

    form = None

    def __init__(self, *args, **kwargs):
        if 'request_addition' in kwargs:
            self.request_addition = kwargs['request_addition']

    def main(self):
        self.request_params = self.get_request()
        CmnLogger.write_log("L7001", 'api')  # start process

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

    def response_api(self, code, params=None) -> Response:
        response, http_status = self.get_response(code, params)

        response = make_response(jsonify(response), http_status)

        # set response header
        for name, value in self.RESPONSE_HEADERS:
            response.headers[name] = value

        return response

    @staticmethod
    def get_response(code: str, params: dict | str | tuple = None) -> tuple:
        if code not in g.params['API_RESPONSE']:
            raise NotFoundConfigException("Not found config [API_RESPONSE][" + code + "]")

        response_config = g.params['API_RESPONSE'][code]
        msg = response_config['MSG']
        http_status = response_config['HTTP']

        if '%' in msg and isinstance(params, dict) is False:
            msg = msg % params

        if 'CODE' in response_config:
            code = response_config['CODE']

        # set default response
        response = {
            'header': {
                'code': code,
                'message': msg
            }
        }

        if isinstance(params, dict):
            response.update(params)

        return response, http_status

    def response_success(self, data: dict = None):
        if data is not None:
            data = {
                'result': data
            }

        return self.response_api(self.CODE_SUCCESS, data)

    def response_create_success(self, data: dict = None):
        if data is not None:
            data = {
                'result': data
            }

        return self.response_api(self.CODE_SUCCESS_CREATE, data)
