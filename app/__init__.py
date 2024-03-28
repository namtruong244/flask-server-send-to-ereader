import os
from flask import Flask, g, jsonify
from flask_cors import CORS
from pymongo import MongoClient

from app.common import CmnError, CmnLogger
from app.utils.util import load_yml_file
from config.flask import app_config

CONFIG_DIRECTORY = 'config/{config_folder}'


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

    @app.errorhandler(Exception)
    def handle_error(e):
        CmnError.handle_exception(e)

    @app.route('/')
    def default_route():
        """Default route"""
        # app.logger.debug('this is a DEBUG message')
        # app.logger.info('this is an INFO message')
        # app.logger.warning('this is a WARNING message')
        # app.logger.error('this is an ERROR message')
        # app.logger.critical('this is a CRITICAL message')
        CmnLogger.write_log('DEV_INFO', ('INFO', 'this is an INFO message'))
        return jsonify('hello world')

    return app


def init_config(config_name):
    config = dict()

    for folder_name in (config_name, 'common'):
        directory = CONFIG_DIRECTORY.format(config_folder=folder_name)

        # iterate over files in that directory
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            data = load_yml_file(file_path)

            if data is not None:
                config.update(data)

    return config
