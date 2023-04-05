import json
import os
import pathlib
import jwt
import datetime
from flask import g
import yaml


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def generation_jwt(payload):
    payload.update({
        'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=24)
    })
    return jwt.encode(payload, g.params['APPLICATION']['SECRET_KEY'], g.params['APPLICATION']['ALGORITHM'])


def load_yml_file(file_directory):
    with open(os.path.join(get_project_root(), file_directory)) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def get_project_root():
    return pathlib.Path(__file__).parent.parent.parent


def parse_json(data):
    return json.loads(data)
