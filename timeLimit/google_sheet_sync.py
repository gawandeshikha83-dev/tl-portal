import gspread
import os


from datetime import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .models import TimeLimit


# ============================================================
# GOOGLE SHEET SETTINGS
# ============================================================

SPREADSHEET_ID = (
    "1tcbuKvziM14fRZLrvgYZtSoVDDrW82DirWWSX2xaGW4"
)

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
    "sheet_token.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


HEADERS = [
    "स.क्र.",
    "TL No.",
    "प्राप्ति दिनांक",
    "प्रेषक",
    "क्र/दिनांक",
    "विषय",
    "संबंधित शाखा का नाम",
    "विवरण",
    "वर्तमान स्थिति",
    "स्थिति",
    "TL PDF",
    "Answer PDF",
]


# ============================================================
# GOOGLE WORKSHEET
# ============================================================

def get_worksheet():

    creds = None

    if os.path.exists(TOKEN_FILE):

        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_FILE,
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open(TOKEN_FILE, "w") as token:

            token.write(
                creds.to_json()
            )

    client = gspread.authorize(
        creds
    )

    spreadsheet = client.open_by_key(
        SPREADSHEET_ID
    )

    worksheet = spreadsheet.sheet1

    return worksheet


# ============================================================
# ENSURE HEADERS
# ============================================================

def ensure_headers(worksheet):

    current_headers = worksheet.row_values(1)

    if not current_headers:
        worksheet.update(
            "A1:L1",
            [HEADERS]
        )

    elif current_headers != HEADERS:

        worksheet.update(
            "A1:L1",
            [HEADERS]
        )


# ============================================================
# DATE FORMAT
# ============================================================

def format_date(value):

    if not value:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%d-%m-%Y")

    return str(value)


# ============================================================
# RECORD → SHEET ROW
# ============================================================

def record_to_row(record):

    return [

        record.sno or "",

        str(record.tl_no or ""),

        format_date(
            record.received_date
        ),

        record.sender_name or "",

        record.letter_no_date or "",

        record.subject or "",

        record.section_name or "",

        record.description or "",

        record.current_situation or "",

        record.current_status or "Pending",

      record.tl_pdf_drive_url or (
    record.tl_pdf.url if record.tl_pdf else ""
),
record.answer_pdf_drive_url or (
    record.answer_pdf.url if record.answer_pdf else ""
),

    ]


# ============================================================
# FIND ROW BY TL NO
# ============================================================

def find_row_by_tl_no(
    worksheet,
    tl_no
):

    target = str(
        tl_no or ""
    ).strip()

    if not target:
        return None

    values = worksheet.col_values(2)

    for row_number, value in enumerate(
        values,
        start=1
    ):

        if row_number == 1:
            continue

        if str(value).strip() == target:
            return row_number

    return None


# ============================================================
# PORTAL → GOOGLE SHEET
# ============================================================

def save_record_to_sheet(record):

    worksheet = get_worksheet()

    ensure_headers(
        worksheet
    )

    row_data = record_to_row(
        record
    )

    existing_row = find_row_by_tl_no(
        worksheet,
        record.tl_no
    )

    if existing_row:

        worksheet.update(
            f"A{existing_row}:L{existing_row}",
            [row_data],
            value_input_option="USER_ENTERED"
        )

    else:

        worksheet.append_row(
            row_data,
            value_input_option="USER_ENTERED"
        )


# ============================================================
# DELETE FROM GOOGLE SHEET
# ============================================================

def delete_record_from_sheet(
    tl_no
):

    worksheet = get_worksheet()

    row_number = find_row_by_tl_no(
        worksheet,
        tl_no
    )

    if row_number:

        worksheet.delete_rows(
            row_number
        )


# ============================================================
# PARSE DATE
# ============================================================

def parse_date(value):

    if not value:
        return None

    if hasattr(value, "date"):
        return value.date()

    value = str(
        value
    ).strip()

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
    ]

    for date_format in formats:

        try:

            return datetime.strptime(
                value,
                date_format
            ).date()

        except ValueError:
            continue

    return None


# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(value):

    try:

        return int(
            float(value)
        )

    except (
        TypeError,
        ValueError
    ):

        return 0


# ============================================================
# GOOGLE SHEET → PORTAL
# ============================================================

def sync_sheet_to_portal():

    worksheet = get_worksheet()

    ensure_headers(
        worksheet
    )

    rows = worksheet.get_all_records()

    imported = 0
    updated = 0

    for row in rows:

        # ----------------------------------------------------
        # TL NO
        # ----------------------------------------------------

        tl_no = str(
            row.get(
                "TL No.",
                ""
            )
        ).strip()

        if not tl_no:
            continue

        # ----------------------------------------------------
        # DATE
        # ----------------------------------------------------

        received_date = parse_date(
            row.get(
                "प्राप्ति दिनांक",
                ""
            )
        )

        if not received_date:
            continue

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = str(
            row.get(
                "स्थिति",
                "Pending"
            )
        ).strip()

        if status not in [
            "Pending",
            "Disposed"
        ]:

            status = "Pending"

        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        defaults = {

            "sno": safe_int(
                row.get(
                    "स.क्र.",
                    0
                )
            ),

            "received_date":
                received_date,

            "sender_name": str(
                row.get(
                    "प्रेषक",
                    ""
                )
            ).strip(),

            "letter_no_date": str(
                row.get(
                    "क्र/दिनांक",
                    ""
                )
            ).strip(),

            "subject": str(
                row.get(
                    "विषय",
                    ""
                )
            ).strip(),

            "section_name": str(
                row.get(
                    "संबंधित शाखा का नाम",
                    ""
                )
            ).strip(),

            "description": str(
                row.get(
                    "विवरण",
                    ""
                )
            ).strip(),

            "current_situation": str(
                row.get(
                    "वर्तमान स्थिति",
                    ""
                )
            ).strip(),

            "current_status":
                status,

        }

        # ----------------------------------------------------
        # EXISTING RECORD
        # ----------------------------------------------------

        record = (
            TimeLimit.objects
            .filter(
                tl_no=tl_no
            )
            .first()
        )

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        if record:

            changed = False

            for field, value in defaults.items():

                if getattr(
                    record,
                    field
                ) != value:

                    setattr(
                        record,
                        field,
                        value
                    )

                    changed = True

            if changed:

                record.save()

                updated += 1

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        else:

            TimeLimit.objects.create(

                tl_no=tl_no,

                **defaults

            )

            imported += 1

    return imported, updated