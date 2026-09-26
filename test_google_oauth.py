from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials/oauth_client.json",
    SCOPES
)

creds = flow.run_local_server(port=0)

with open("credentials/token.json", "w") as token:
    token.write(creds.to_json())

print("Google OAuth successful!")
print("token.json created successfully.")