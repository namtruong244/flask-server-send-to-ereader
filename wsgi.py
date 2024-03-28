import os
from app import create_app
from dotenv import load_dotenv
from app.common import CmnLogger

load_dotenv()
config_name = os.getenv('APPLICATION_ENV')
app = create_app(config_name)

if __name__ != '__main__':
    # gunicorn_logger = logging.getLogger('gunicorn.error')
    # app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)
    CmnLogger.setup_logging()

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run()
