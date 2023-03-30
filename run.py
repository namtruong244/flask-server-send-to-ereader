import os
from app import create_app
from dotenv import load_dotenv

load_dotenv()
config_name = os.getenv('APPLICATION_ENV')
app = create_app(config_name)

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run('localhost', port=8000)
    print(app.url_map)
