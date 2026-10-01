import os
import json

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


SCOPES = [
    "https://www.googleapis.com/auth/drive"
]


# Google Drive folders
TL_PDF_FOLDER_ID = "1Q1E_PxdPTOPwIm6i10fVtwWRaZdbcRe1"
ANSWER_PDF_FOLDER_ID = "1xQRodxwqAwRu1ILnlM_INKmYaiDrTiuM"


def get_drive_service():

    google_credentials = os.environ.get("GOOGLE_CREDENTIALS")

    if not google_credentials:
        raise ValueError(
            "GOOGLE_CREDENTIALS environment variable is missing."
        )

    try:
        data = json.loads(google_credentials)
    except json.JSONDecodeError as e:
        raise ValueError(
            "GOOGLE_CREDENTIALS is not valid JSON."
        ) from e

    if data.get("type") != "service_account":
        raise ValueError(
            "GOOGLE_CREDENTIALS must contain a Google Service Account JSON."
        )

    credentials = Credentials.from_service_account_info(
        data,
        scopes=SCOPES
    )

    return build(
        "drive",
        "v3",
        credentials=credentials
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

    uploaded_file = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id,name,webViewLink,webContentLink"
        )
        .execute()
    )

    file_id = uploaded_file.get("id")

    # Allow users to open the PDF through the Drive link
    service.permissions().create(
        fileId=file_id,
        body={
            "type": "anyone",
            "role": "reader"
        }
    ).execute()

    # Get the final links again
    uploaded_file = (
        service.files()
        .get(
            fileId=file_id,
            fields="id,name,webViewLink,webContentLink"
        )
        .execute()
    )

    return uploaded_file