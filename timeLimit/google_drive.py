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

TL_PDF_FOLDER_ID = "1Q1E_PxdPTOPwIm6i10fVtwWRaZdbcRe1"
ANSWER_PDF_FOLDER_ID = "1xQRodxwqAwRu1ILnlM_INKmYaiDrTiuM"


def get_credentials():
    google_credentials = os.environ.get("GOOGLE_CREDENTIALS")

    if google_credentials:
        data = json.loads(google_credentials)

        if "token" in data and "refresh_token" in data:
            creds = Credentials.from_authorized_user_info(
                data,
                SCOPES
            )
        else:
            raise ValueError(
                "GOOGLE_CREDENTIALS does not contain a valid OAuth token."
            )

    else:
        token_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "credentials",
            "token.json"
        )

        if not os.path.exists(token_path):
            raise FileNotFoundError(
                "OAuth token.json not found."
            )

        with open(token_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        creds = Credentials.from_authorized_user_info(
            data,
            SCOPES
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
        "parents": [folder_id]
    }

    media = MediaIoBaseUpload(
        file_obj,
        mimetype="application/pdf",
        resumable=True
    )

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,name,webViewLink,webContentLink"
    ).execute()

    file_id = uploaded_file.get("id")

    service.permissions().create(
        fileId=file_id,
        body={
            "type": "anyone",
            "role": "reader"
        }
    ).execute()

    return service.files().get(
        fileId=file_id,
        fields="id,name,webViewLink,webContentLink"
    ).execute()