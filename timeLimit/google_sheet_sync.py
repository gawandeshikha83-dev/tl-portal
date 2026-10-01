import requests
from datetime import datetime

GOOGLE_SHEET_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwkkVspWfHe_ME3egCpERrPynXcve-8Cg6HCmDkkGIM6gMebEuDbq3OEFH9HRAkwS7xog"
    "/exec"
)


# ============================================================
# CONVERT DJANGO RECORD → GOOGLE SHEET RECORD
# ============================================================

def record_to_sheet_data(record):

    received_date = ""

    if record.received_date:
        received_date = record.received_date.strftime("%Y-%m-%d")

    return {
        "स.क्र.": record.sno,
        "TL No.": record.tl_no or "",
        "प्राप्ति दिनांक": received_date,
        "प्रेषक": record.sender_name or "",
        "क्र/दिनांक": record.letter_no_date or "",
        "विषय": record.subject or "",
        "संबंधित शाखा का नाम": record.section_name or "",
        "विवरण": record.description or "",
        "वर्तमान स्थिति": record.current_situation or "",
        "स्थिति": record.current_status or "Pending",

        # Google Drive links
        "TL PDF": record.tl_pdf_drive_url or "",
        "Answer PDF": record.answer_pdf_drive_url or "",
    }


# ============================================================
# ADD / UPDATE RECORD IN GOOGLE SHEET
# ============================================================

def save_record_to_sheet(record, old_tl_no=None):

    data = record_to_sheet_data(record)

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    if old_tl_no:

        payload = {
            "action": "update",
            "old_tl_no": str(old_tl_no),
            "record": data,
        }

    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    else:

        payload = {
            "action": "add",
            "record": data,
        }

    response = requests.post(
        GOOGLE_SHEET_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("success") is False:

        raise Exception(
            result.get(
                "error",
                "Google Sheet update failed."
            )
        )

    print(
        "GOOGLE SHEET SYNC:",
        result
    )

    return result


# ============================================================
# DELETE RECORD FROM GOOGLE SHEET
# ============================================================

def delete_record_from_sheet(tl_no):

    payload = {
        "action": "delete",
        "tl_no": str(tl_no),
    }

    response = requests.post(
        GOOGLE_SHEET_URL,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("success") is False:

        raise Exception(
            result.get(
                "error",
                "Google Sheet delete failed."
            )
        )

    print(
        "GOOGLE SHEET DELETE:",
        result
    )

    return result


# ============================================================
# GET DATA FROM GOOGLE SHEET
# ============================================================

def get_google_sheet_data():

    response = requests.get(
        GOOGLE_SHEET_URL,
        timeout=30,
    )

    response.raise_for_status()

    records = response.json()

    # Apps Script error response
    if isinstance(records, dict):

        if records.get("success") is False:

            raise Exception(
                records.get(
                    "error",
                    "Google Sheet read failed."
                )
            )

        records = records.get(
            "data",
            []
        )

    cleaned_records = []

    for row in records:

        def clean_date(value):

            if not value:
                return None

            if hasattr(value, "date"):
                return value.date()

            try:

                return datetime.fromisoformat(
                    str(value).replace(
                        "Z",
                        "+00:00"
                    )
                ).date()

            except Exception:

                try:

                    return datetime.strptime(
                        str(value),
                        "%Y-%m-%d"
                    ).date()

                except Exception:

                    return None

        cleaned_records.append({

            "sno": row.get(
                "स.क्र."
            ),

            "tl_no": row.get(
                "TL No.",
                ""
            ),

            "received_date": clean_date(
                row.get(
                    "प्राप्ति दिनांक"
                )
            ),

            "sender_name": row.get(
                "प्रेषक",
                ""
            ),

            "letter_no_date": row.get(
                "क्र/दिनांक",
                ""
            ),

            "subject": row.get(
                "विषय",
                ""
            ),

            "section_name": row.get(
                "संबंधित शाखा का नाम",
                ""
            ),

            "description": row.get(
                "विवरण",
                ""
            ),

            "current_situation": row.get(
                "वर्तमान स्थिति",
                ""
            ),

            "current_status": row.get(
                "स्थिति",
                "Pending"
            ),

            "tl_pdf_drive_url": row.get(
                "TL PDF",
                ""
            ),

            "answer_pdf_drive_url": row.get(
                "Answer PDF",
                ""
            ),
        })

    return cleaned_records


# ============================================================
# GOOGLE SHEET → PORTAL
# ============================================================

def sync_sheet_to_portal():

    from .models import TimeLimit

    sheet_records = get_google_sheet_data()

    synced_count = 0

    for data in sheet_records:

        tl_no = str(
            data.get(
                "tl_no",
                ""
            )
        ).strip()

        if not tl_no:
            continue

        defaults = {

            "sno": data.get(
                "sno"
            ),

            "received_date": data.get(
                "received_date"
            ),

            "sender_name": data.get(
                "sender_name",
                ""
            ),

            "letter_no_date": data.get(
                "letter_no_date",
                ""
            ),

            "subject": data.get(
                "subject",
                ""
            ),

            "section_name": data.get(
                "section_name",
                ""
            ),

            "description": data.get(
                "description",
                ""
            ),

            "current_situation": data.get(
                "current_situation",
                ""
            ),

            "current_status": data.get(
                "current_status",
                "Pending"
            ),

            "tl_pdf_drive_url": data.get(
                "tl_pdf_drive_url",
                ""
            ),

            "answer_pdf_drive_url": data.get(
                "answer_pdf_drive_url",
                ""
            ),
        }

        record, created = TimeLimit.objects.update_or_create(

            tl_no=tl_no,

            defaults=defaults,
        )

        synced_count += 1

    print(
        f"GOOGLE SHEET → PORTAL: "
        f"{synced_count} records synced."
    )

    return synced_count