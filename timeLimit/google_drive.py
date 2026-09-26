import os

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLIENT_FILE = os.path.join(
    BASE_DIR,
    "..",
    "credentials",
    "oauth_client.json"
)

TOKEN_FILE = os.path.join(
    BASE_DIR,
    "..",
    "credentials",
    "token.json"
)

# Google Drive folders
TL_PDF_FOLDER_ID = "1Q1E_PxdPTOPwIm6i10fVtwWRaZdbcRe1"
ANSWER_PDF_FOLDER_ID = "1xQRodxwqAwRu1ILnlM_INKmYaiDrTiuM"


def get_drive_service():

    creds = None

    # Existing OAuth token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    # Token invalid/expired
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_FILE,
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save updated token
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build(
        "drive",
        "v3",
        credentials=creds
    )


def upload_file_to_drive(file_obj, file_name, folder_id):

    service = get_drive_service()

    file_metadata = {
        "name": file_name,
        "parents": [folder_id],
    }

    media = MediaIoBaseUpload(
        file_obj,
        mimetype="application/pdf",
        resumable=True
    )

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, name, webViewLink, webContentLink"
    ).execute()

    return uploaded_file