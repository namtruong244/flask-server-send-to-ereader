import json
import os
import pathlib
from functools import wraps

import google
import google_auth_oauthlib.flow
import jwt
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from dotenv import load_dotenv
from flask import Flask, request, g
from flask.wrappers import Response
from flask_cors import CORS
from google.auth.transport import requests
from google.oauth2 import id_token
from pymongo import MongoClient

from src.utils.util import generation_jwt, credentials_to_dict

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = os.path.join(pathlib.Path(__file__).parent, 'src/config/client-secret.json')
CLIENT_ID = '611402686764-ihcj8p6dnpv3gsk7t20rnadec94nfrdj.apps.googleusercontent.com'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
]
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

app = Flask(__name__)
load_dotenv()
CORS(app)
app.config['Access-Control-Allow-Origin'] = '*'
app.config['Access-Control-Allow-Headers'] = 'Content-Type'

# Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    client_secrets_file=CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri='postmessage'
)


# wrapper
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'Authorization' in request.headers:
            token = request.headers.get('Authorization').split('Bearer ')[1]

        # Return 401 if token is not passed
        if token is None:
            return Response(
                        response=json.dumps({'message': 'Token is missing'}),
                        status=401,
                        mimetype='application/json'
                    )

        try:
            # decoding the payload to fetch the stored details
            decoded_jwt = jwt.decode(token, 'SecretKey', ['HS256'])
            user_collection = g.mongo_client['send_to_ereader']['users']
            current_user = user_collection.find_one({
                '_id': decoded_jwt['id']
            })
        except Exception as e:
            print(e.args)
            return Response(
                        response=json.dumps({'message': 'Token is missing'}),
                        status=401,
                        mimetype='application/json'
                    )

        # returns the current logged users context to the routes
        return function(current_user, *args, **kwargs)

    return wrapper


@app.route('/authorize', methods=['POST'])
def authorize():
    body = request.get_json(force=True)
    flow.fetch_token(code=body['code'])
    credentials = flow.credentials

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=requests.Request(),
        audience=CLIENT_ID
    )

    user_collection = g.mongo_client['send_to_ereader']['users']
    user_collection.update_one(
        filter={'_id': id_info['sub']},
        update={
            '$set': {
                '_id': id_info['sub'],
                'email': id_info['email'],
                'name': id_info['name'],
                'picture': id_info['picture'],
                'credentials': credentials_to_dict(credentials)
            }
        },
        upsert=True
    )

    jwt_token = generation_jwt({
        'id': id_info['sub'],
        'email': id_info['email'],
        'name': id_info['name']
    })

    return Response(
        response=json.dumps({'JWT': jwt_token}),
        status=200,
        mimetype='application/json'
    )


@app.route('/get-folders-drive')
@login_required
def get_folders_drive(current_user):

    try:
        # Load credentials from the Database.
        credentials = google.oauth2.credentials.Credentials(
            **current_user['credentials'])

        drive = build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=credentials
        )

        folders = []
        page_token = None
        query = "mimeType='application/vnd.google-apps.folder' and '{email}' in owners".format(email=current_user['email'])
        while True:
            # pylint: disable=maybe-no-member
            response = drive.files().list(
                q=query,
                spaces='drive',
                fields='nextPageToken, '
                       ' files(id, name)',
                pageToken=page_token
            ).execute()

            folders.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)

            if page_token is None:
                break

    except HttpError as e:
        print(e)
        return Response(
            response=json.dumps({'message': 'System Error'}),
            status=500,
            mimetype='application/json'
        )

    return Response(
        response=json.dumps({'folders': folders}),
        status=200,
        mimetype='application/json'
    )


@app.before_request
def before_request():
    client = get_db()
    g.mongo_client = client


@app.after_request
def after_request(response):
    g.mongo_client.close()
    return response


def get_db():
    connection_string = 'mongodb://localhost:27017'
    client = MongoClient(connection_string)
    return client


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run('localhost', port=8080)
