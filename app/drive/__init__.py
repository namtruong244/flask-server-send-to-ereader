from flask import Blueprint
from app.common.decorators import login_required
from app.drive.get_folders_drive_controller import GetFoldersDriveController

drive = Blueprint('drive', __name__)


@drive.route('/drive/folders', methods=('POST',))
@login_required
def get_folders(current_user):
    return GetFoldersDriveController(request_addition={'current_user': current_user}).main()
