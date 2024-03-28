import json
import os

import google_auth_oauthlib.flow
from flask import g, Response
from google.oauth2 import id_token
from google.auth.transport import requests

from ..collection.users_collection import UsersCollection
from ..common.cmn_controller import CmnController
from ..utils.util import credentials_to_dict, get_project_root, generation_jwt


class AuthorizeGoogleController(CmnController):

    def execute(self):
        application_config = g.params['APPLICATION']
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        client_secrets_file = os.path.join(get_project_root(), application_config['CLIENT_SECRETS_FILE'])
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            client_secrets_file=client_secrets_file,
            scopes=application_config['GOOGLE_API_SCOPES'],
            redirect_uri='postmessage'
        )

        flow.fetch_token(code=self.request_params['code'])
        credentials = flow.credentials

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=requests.Request(),
            audience=application_config['CLIENT_ID']
        )

        user_collection = UsersCollection()
        user_collection.collection.update_one(
            filter={'_id': id_info['sub']},
            update={
                '$set': {
                    '_id': id_info['sub'],
                    'email': id_info['email'],
                    'name': id_info['name'],
                    'picture': id_info['picture'],
                    'credentials': credentials_to_dict(credentials)
                }
            }, upsert=True)

        jwt_token = generation_jwt({
            'id': id_info['sub'],
            'email': id_info['email'],
            'name': id_info['name']
        })
        # return {'JWT': jwt_token}
        return Response(response=json.dumps({'JWT': jwt_token}), status=200, mimetype='application/json')
