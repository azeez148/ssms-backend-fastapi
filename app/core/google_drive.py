from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

class GoogleDriveService:
    def __init__(self, client_secrets_path='client_secrets.json', credentials_path='mycreds.txt'):
        self.client_secrets_path = client_secrets_path
        self.credentials_path = credentials_path
        self.drive = self._authenticate()

    def _authenticate(self):
        gauth = GoogleAuth()
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(self.credentials_path)
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(self.credentials_path)
        return GoogleDrive(gauth)

    def upload_image(self, file_path, folder_id=None):
        """
        Uploads an image to Google Drive and returns the shareable link.
        - file_path: Path to the local file to upload.
        - folder_id: The ID of the folder in Google Drive to upload the file to.
                     If None, it uploads to the root folder.
        """
        file_name = os.path.basename(file_path)

        file_metadata = {'title': file_name}
        if folder_id:
            file_metadata['parents'] = [{'id': folder_id}]

        drive_file = self.drive.CreateFile(file_metadata)
        drive_file.SetContentFile(file_path)
        drive_file.Upload()

        # Make the file publicly readable
        drive_file.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })

        return drive_file['alternateLink']
