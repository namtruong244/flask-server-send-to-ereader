import google
from ..common.cmn_controller import CmnController
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import g


class GetFoldersDriveController(CmnController):

    def execute(self):
        # Load credentials from the Database.
        credentials = google.oauth2.credentials.Credentials(
            **self.request_params['current_user']['credentials']
        )

        drive_service = build(
            g.params['APPLICATION']['GOOGLE_API_SERVICE_NAME'],
            g.params['APPLICATION']['GOOGLE_API_VERSION'],
            credentials=credentials
        )

        folders = []
        page_token = None
        query = "mimeType='application/vnd.google-apps.folder' and '{email}' in owners".format(email=self.request_params['current_user']['email'])
        while True:
            response = drive_service.files().list(
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

        response = {
            'folders': folders
        }
        return self.response_success(response)
