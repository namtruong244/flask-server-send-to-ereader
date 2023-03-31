import jwt
from functools import wraps
from flask import request, g, make_response, jsonify


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
            return '401'

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
            user_collection = g.mongo_client[g.params['APPLICATION']['DATABASE_NAME']]['users']
            current_user = user_collection.find_one({
                '_id': decoded_jwt['id']
            })
        except Exception as e:
            print(e.args)
            return make_response(jsonify({'message': 'Error jwt'}), 401)

        # returns the current logged users context to the routes
        return function(current_user, *args, **kwargs)

    return wrapper
