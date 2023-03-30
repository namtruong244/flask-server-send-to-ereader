from flask import Blueprint
from .authorize_google_controller import AuthorizeGoogleController

auth = Blueprint('auth', __name__)


@auth.route('/authorize/google', methods=('POST',))
def authorize_google():
    return AuthorizeGoogleController().main()
