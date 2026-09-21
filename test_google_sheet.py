import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(
    "credentials/service-account.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1tcbuKvziM14fRZLrvgYZtSoVDDrW82DirWWSX2xaGW4"
)

worksheet = sheet.sheet1

print("Google Sheet Connection SUCCESS!")
print("Sheet Name:", worksheet.title)
print("Rows found:", len(worksheet.get_all_records()))

print("\nData:")
for row in worksheet.get_all_records():
    print(row)