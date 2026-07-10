# gmail_reader.py
import os
import json
import base64
from datetime import datetime, timedelta

import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# This is the "permission level" we're asking Gmail for
# Read-only means the agent can only READ, never delete or send
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def get_gmail_service():
    creds = None

    # ✅ CLOUD: Try loading from Streamlit secrets first (safely!)
    try:
        if "gmail_token" in st.secrets:
            token_data = json.loads(st.secrets["gmail_token"]["token_json"])
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    except (FileNotFoundError, KeyError):
        pass  # No secrets file locally — that's fine, we'll use token.json instead

    # ✅ LOCAL: Fall back to local token.json file
    if not creds and os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid creds, refresh or do a fresh login (local only)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save login for next time (local only)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)




def get_todays_emails(max_emails=20, mark_read=True):
    """Fetches today's emails from Gmail, and optionally marks them as read."""
    service = get_gmail_service()

    today = datetime.now().strftime('%Y/%m/%d')
    query = f'after:{today}'

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
        full_msg = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = full_msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

        body = extract_body(full_msg['payload'])

        emails.append({
            'subject': subject,
            'from': sender,
            'body': body[:1000]
        })

        # ✅ Mark this email as read right after processing it
        if mark_read:
            mark_as_read(service, msg['id'])

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

def mark_as_read(service, message_id):
    """Removes the UNREAD label from an email — marks it as read."""
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()