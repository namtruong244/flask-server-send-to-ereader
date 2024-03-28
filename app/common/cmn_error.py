from flask import make_response, jsonify
from app.common.cmn_controller import CmnController


class CmnError:
    @staticmethod
    def handle_exception(e):
        code = '25999'

        response, status_code = CmnController.get_response(code)
        response = make_response(jsonify(response), status_code)

        # set response headers
        for name, value in CmnController.RESPONSE_HEADERS:
            response.headers[name] = value

        return response
