import jwt
from functools import wraps
from flask import request, g, make_response, jsonify

from app.collection.users_collection import UsersCollection
from app.common.cmn_controller import CmnController


# wrapper
def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization').split(f"{g.params['APPLICATION']['SECRET_TYPE']} ")[1]

        # Return 401 if token is not passed
        if token is None:
            response, http_status = CmnController.get_response('40002')
            return make_response(jsonify(response), http_status)

        try:
            # decoding the payload to fetch the stored details
            options = {
                'verify_exp': True
            }
            decoded_jwt = jwt.decode(
                token,
                g.params['APPLICATION']['SECRET_KEY'],
                g.params['APPLICATION']['ALGORITHM'],
                options=options
            )
            user_collection = UsersCollection()
            current_user = user_collection.collection.find_one({
                '_id': decoded_jwt['id']
            })
        except Exception as e:
            print(e.args)
            response, http_status = CmnController.get_response('40001')
            return make_response(jsonify(response), http_status)

        # returns the current logged users context to the routes
        return function(current_user, *args, **kwargs)

    return wrapper
