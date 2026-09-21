import requests
from datetime import datetime


GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbwkkVspWfHe_ME3egCpERrPynXcve-8Cg6HCmDkkGIM6gMebEuDbq3OEFH9HRAkwS7xog/exec"


def get_google_sheet_data():
    """
    Google Sheet se TL records read karta hai
    aur Django ke liye clean format return karta hai.
    """

    response = requests.get(
        GOOGLE_SHEET_URL,
        timeout=20
    )

    response.raise_for_status()

    records = response.json()

    cleaned_records = []

    for row in records:

        def clean_date(value):
            if not value:
                return None

            try:
                # Google Sheet API date format:
                # 2026-09-08T18:30:00.000Z
                dt = datetime.fromisoformat(
                    value.replace("Z", "+00:00")
                )

                return dt.date()

            except Exception:
                return value

        cleaned_records.append({
            "sno": row.get("स.क्र."),
            "tl_no": row.get("TL No."),
            "received_date": clean_date(
                row.get("प्राप्ति दिनांक")
            ),
            "sender_name": row.get("प्रेषक", ""),
            "letter_no_date": row.get("क्र/दिनांक", ""),
            "subject": row.get("विषय", ""),
            "section_name": row.get(
                "संबंधित शाखा का नाम", ""
            ),
            "description": row.get("विवरण", ""),
            "current_situation": row.get(
                "वर्तमान स्थिति", ""
            ),
            "current_status": row.get(
                "स्थिति", "Pending"
            ),
            "tl_pdf": row.get("TL PDF", ""),
            "answer_pdf": row.get(
                "Answer PDF", ""
            ),
        })

    return cleaned_records