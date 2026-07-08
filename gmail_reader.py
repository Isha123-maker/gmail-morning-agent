# gmail_reader.py
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from datetime import datetime, timedelta

# This is the "permission level" we're asking Gmail for
# Read-only means the agent can only READ, never delete or send
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Sets up connection to Gmail. Like logging in, but for robots."""
    creds = None

    # If we've logged in before, reuse that saved login
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no saved login or it expired, do a fresh login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save login for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def get_todays_emails(max_emails=20):
    """Fetches today's emails from Gmail."""
    service = get_gmail_service()

    # Get today's date in Gmail search format
    today = datetime.now().strftime('%Y/%m/%d')
    query = f'after:{today}'

    # Search Gmail for today's emails
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_emails
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        return []

    emails = []
    for msg in messages:
        # Fetch full email details
        full_msg = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        # Extract subject and sender from headers
        headers = full_msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

        # Extract email body text
        body = extract_body(full_msg['payload'])

        emails.append({
            'subject': subject,
            'from': sender,
            'body': body[:1000]  # Limit to 1000 chars per email
        })

    return emails


def extract_body(payload):
    """Pulls the actual text out of the email."""
    body = ""

    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    return body.strip()