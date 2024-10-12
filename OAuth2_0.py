import os
import pickle
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Path to your client_secrets.json file from the Google Developer Console
CLIENT_SECRETS_FILE = 'client_secrets.json'

# Scopes required for Gmail API to send emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_token():
    creds = None
    token_path = 'token.pickle'

    # Check if token.pickle exists (saved credentials)
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials available, request new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Function to get access token
def get_access_token():
    creds = get_gmail_token()
    return creds.token


