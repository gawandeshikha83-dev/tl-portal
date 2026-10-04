import requests
from datetime import datetime


GOOGLE_SHEET_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwkkVspWfHe_ME3egCpERrPynXcve-8Cg6HCmDkkGIM6gMebEuDbq3OEFH9HRAkwS7xog"
    "/exec"
)


# ============================================================
# DJANGO RECORD → GOOGLE SHEET DATA
# ============================================================



def record_to_sheet_data(record):
    received_date = ""

    if record.received_date:
        received_date = record.received_date.strftime("%Y-%m-%d")

    return {
        "sno": record.sno,
        "tl_no": record.tl_no or "",
        "received_date": received_date,
        "sender_name": record.sender_name or "",
        "letter_no_date": record.letter_no_date or "",
        "subject": record.subject or "",
        "section_name": record.section_name or "",
        "description": record.description or "",
        "current_situation": record.current_situation or "",
        "current_status": record.current_status or "Pending",
        "tl_pdf_drive_url": record.tl_pdf_drive_url or "",
        "answer_pdf_drive_url": record.answer_pdf_drive_url or "",
    }

# ============================================================
# SAVE / UPDATE → GOOGLE SHEET
# ============================================================

def save_record_to_sheet(record, old_tl_no=None):

    data = record_to_sheet_data(record)

    if old_tl_no:

        payload = {
            "action": "update",
            "old_tl_no": str(old_tl_no),
            "record": data,
        }

    else:

        payload = {
            "action": "add",
            "record": data,
        }

    print("GOOGLE SHEET REQUEST:", payload)

    response = requests.post(
        GOOGLE_SHEET_URL,
        json=payload,
        timeout=30,
    )

    print(
        "GOOGLE SHEET RESPONSE:",
        response.status_code,
        response.text[:1000],
    )

    response.raise_for_status()

    result = response.json()

    if result.get("success") is False:

        raise Exception(
            result.get(
                "error",
                "Google Sheet update failed.",
            )
        )

    print(
        "GOOGLE SHEET SYNC:",
        result,
    )

    return result


# ============================================================
# DELETE → GOOGLE SHEET
# ============================================================

def delete_record_from_sheet(tl_no):

    payload = {
        "action": "delete",
        "tl_no": str(tl_no),
    }

    print(
        "GOOGLE SHEET DELETE REQUEST:",
        payload,
    )

    response = requests.post(
        GOOGLE_SHEET_URL,
        json=payload,
        timeout=30,
    )

    print(
        "GOOGLE SHEET DELETE RESPONSE:",
        response.status_code,
        response.text[:1000],
    )

    response.raise_for_status()

    result = response.json()

    if result.get("success") is False:

        raise Exception(
            result.get(
                "error",
                "Google Sheet delete failed.",
            )
        )

    print(
        "GOOGLE SHEET DELETE:",
        result,
    )

    return result


# ============================================================
# DATE CLEANING
# ============================================================

def clean_date(value):

    if not value:
        return None

    if hasattr(value, "date"):
        return value.date()

    value = str(value).strip()

    if not value:
        return None

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
    ]

    for date_format in formats:

        try:

            return datetime.strptime(
                value,
                date_format,
            ).date()

        except ValueError:
            continue

    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        ).date()

    except Exception:

        return None


# ============================================================
# GOOGLE SHEET → PYTHON DATA
# ============================================================

def get_google_sheet_data():

    print(
        "GOOGLE SHEET GET:",
        GOOGLE_SHEET_URL,
    )

    response = requests.get(
        GOOGLE_SHEET_URL,
        timeout=30,
        allow_redirects=True,
    )

    print(
        "GOOGLE SHEET GET STATUS:",
        response.status_code,
    )

    print(
        "GOOGLE SHEET GET RESPONSE:",
        response.text[:2000],
    )

    response.raise_for_status()

    records = response.json()

    if isinstance(records, dict):

        if records.get("success") is False:

            raise Exception(
                records.get(
                    "error",
                    "Google Sheet read failed.",
                )
            )

        records = records.get(
            "data",
            [],
        )

    if not isinstance(records, list):

        raise Exception(
            "Google Sheet response is not a list."
        )

    print(
        "GOOGLE SHEET RECORD COUNT:",
        len(records),
    )

    cleaned_records = []

    for row in records:

        if not isinstance(row, dict):
            continue

        tl_no = str(
            row.get(
                "TL No.",
                "",
            )
        ).strip()

        if not tl_no:
            continue

        cleaned_records.append({

            "sno": row.get(
                "स.क्र.",
                "",
            ),

            "tl_no": tl_no,

            "received_date": clean_date(
                row.get(
                    "प्राप्ति दिनांक",
                    "",
                )
            ),

            "sender_name": row.get(
                "प्रेषक",
                "",
            ),

            "letter_no_date": row.get(
                "क्र/दिनांक",
                "",
            ),

            "subject": row.get(
                "विषय",
                "",
            ),

            "section_name": row.get(
                "संबंधित शाखा का नाम",
                "",
            ),

            "description": row.get(
                "विवरण",
                "",
            ),

            "current_situation": row.get(
                "वर्तमान स्थिति",
                "",
            ),

            "current_status": (
                row.get(
                    "स्थिति",
                    "Pending",
                )
                or "Pending"
            ),

            "tl_pdf_drive_url": str(
                row.get(
                    "TL PDF",
                    "",
                )
                or ""
            ).strip(),

            "answer_pdf_drive_url": str(
                row.get(
                    "Answer PDF",
                    "",
                )
                or ""
            ).strip(),
        })

    print(
        "CLEANED GOOGLE SHEET RECORDS:",
        len(cleaned_records),
    )

    return cleaned_records


# ============================================================
# GOOGLE SHEET → PORTAL
# ============================================================

def sync_sheet_to_portal():

    from .models import TimeLimit

    # ========================================================
    # GOOGLE SHEET DATA
    # ========================================================

    sheet_records = get_google_sheet_data()

    synced_count = 0

    # Sheet में मौजूद सभी TL Numbers
    sheet_tl_nos = set()

    for data in sheet_records:

        tl_no = str(
            data.get(
                "tl_no",
                "",
            )
        ).strip()

        if not tl_no:
            continue

        sheet_tl_nos.add(tl_no)

        try:

            record = TimeLimit.objects.filter(
                tl_no=tl_no,
            ).first()

            # =================================================
            # EXISTING RECORD
            # =================================================

            if record:

                record.sno = data.get("sno")

                record.received_date = data.get(
                    "received_date"
                )

                record.sender_name = data.get(
                    "sender_name",
                    "",
                )

                record.letter_no_date = data.get(
                    "letter_no_date",
                    "",
                )

                record.subject = data.get(
                    "subject",
                    "",
                )

                record.section_name = data.get(
                    "section_name",
                    "",
                )

                record.description = data.get(
                    "description",
                    "",
                )

                record.current_situation = data.get(
                    "current_situation",
                    "",
                )

                record.current_status = data.get(
                    "current_status",
                    "Pending",
                ) or "Pending"

                # ---------------------------------------------
                # PDF URL
                # Blank Sheet URL existing URL को erase
                # नहीं करेगा.
                # ---------------------------------------------

                if data.get("tl_pdf_drive_url"):

                    record.tl_pdf_drive_url = data.get(
                        "tl_pdf_drive_url"
                    )

                if data.get("answer_pdf_drive_url"):

                    record.answer_pdf_drive_url = data.get(
                        "answer_pdf_drive_url"
                    )

                record.save()

                print(
                    "SYNCED EXISTING:",
                    tl_no,
                )

            # =================================================
            # NEW RECORD
            # =================================================

            else:

                TimeLimit.objects.create(

                    sno=data.get("sno"),

                    tl_no=tl_no,

                    received_date=data.get(
                        "received_date"
                    ),

                    sender_name=data.get(
                        "sender_name",
                        "",
                    ),

                    letter_no_date=data.get(
                        "letter_no_date",
                        "",
                    ),

                    subject=data.get(
                        "subject",
                        "",
                    ),

                    section_name=data.get(
                        "section_name",
                        "",
                    ),

                    description=data.get(
                        "description",
                        "",
                    ),

                    current_situation=data.get(
                        "current_situation",
                        "",
                    ),

                    current_status=data.get(
                        "current_status",
                        "Pending",
                    ) or "Pending",

                    tl_pdf_drive_url=data.get(
                        "tl_pdf_drive_url",
                        "",
                    ),

                    answer_pdf_drive_url=data.get(
                        "answer_pdf_drive_url",
                        "",
                    ),
                )

                print(
                    "CREATED NEW:",
                    tl_no,
                )

            synced_count += 1

        except Exception as error:

            print(
                "SYNC ERROR:",
                tl_no,
                error,
            )

    # ========================================================
    # DELETE RECORDS
    # ========================================================
    # जो TL Render DB में है लेकिन Google Sheet में नहीं है
    # उसे Render DB से delete किया जाएगा.
    # ========================================================

    deleted_records = TimeLimit.objects.exclude(
        tl_no__in=sheet_tl_nos
    )

    deleted_count = deleted_records.count()

    if deleted_count:

        for record in deleted_records:

            print(
                "DELETING FROM PORTAL:",
                record.tl_no,
            )

        deleted_records.delete()

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "GOOGLE SHEET → PORTAL:",
        f"{synced_count} records synced,",
        f"{deleted_count} records deleted.",
    )

    return synced_count