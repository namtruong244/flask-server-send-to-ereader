from flask import Flask, g
from flask_cors import CORS
from pymongo import MongoClient

from app.utils.util import load_yml_file
from config import app_config

CONFIG_PATH = 'config/{config_name}/application.yml'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.config['Access-Control-Allow-Origin'] = '*'
    app.config['Access-Control-Allow-Headers'] = 'Content-Type'

    CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api')

    from .drive import drive as drive_blueprint
    app.register_blueprint(drive_blueprint, url_prefix='/api')

    @app.before_request
    def before_request():
        g.params = init_config(config_name)
        g.mongo_client = MongoClient(g.params['APPLICATION']['DATABASE_URI'])

    @app.after_request
    def after_request(response):
        if 'mongo_client' in g:
            g.mongo_client.close()

        return response

    return app


def init_config(config_name):
    config = dict()
    data = load_yml_file(CONFIG_PATH.format(config_name=config_name))
    if data is not None:
        config.update(data)

    return config
