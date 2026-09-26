import os
import json
import io

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

# Google Drive folders
TL_PDF_FOLDER_ID = "1Q1E_PxdPTOPwIm6i10fVtwWRaZdbcRe1"
ANSWER_PDF_FOLDER_ID = "1xQRodxwqAwRu1ILnlM_INKmYaiDrTiuM"


def get_credentials():

    google_credentials = os.environ.get("GOOGLE_CREDENTIALS")

    if not google_credentials:
        raise FileNotFoundError(
            "GOOGLE_CREDENTIALS environment variable is missing."
        )

    data = json.loads(google_credentials)

    # Support either a token JSON directly or a credentials wrapper
    if "token" in data and "refresh_token" in data:

        creds = Credentials.from_authorized_user_info(
            data,
            SCOPES
        )

    else:
        raise ValueError(
            "GOOGLE_CREDENTIALS does not contain a valid OAuth token."
        )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


def get_drive_service():

    creds = get_credentials()

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