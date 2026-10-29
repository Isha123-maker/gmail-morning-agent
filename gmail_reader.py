# gmail_reader.py
import os
import json
import base64
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# This is the "permission level" we're asking Gmail for
# Read-only means the agent can only READ, never delete or send
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
PAKISTAN_TIMEZONE = ZoneInfo("Asia/Karachi")


def build_today_query(now=None):
    """Build a Gmail query for the current calendar day in Pakistan time."""
    if now is None:
        now = datetime.now(PAKISTAN_TIMEZONE)
    elif now.tzinfo is None:
        raise ValueError("now must include timezone information")

    local_now = now.astimezone(PAKISTAN_TIMEZONE)
    start_of_day = datetime.combine(local_now.date(), time.min, tzinfo=PAKISTAN_TIMEZONE)
    start_of_tomorrow = start_of_day + timedelta(days=1)

    start_timestamp = int(start_of_day.timestamp())
    tomorrow_timestamp = int(start_of_tomorrow.timestamp())
    return f"after:{start_timestamp} before:{tomorrow_timestamp}"


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




def get_todays_emails(max_emails=20):
    """Fetches today's emails from Gmail without modifying them."""
    service = get_gmail_service()

    query = build_today_query()

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

        payload = full_msg.get('payload') or {}
        headers = payload.get('headers') or []
        subject = next(
            (h.get('value') for h in headers if h.get('name', '').lower() == 'subject' and h.get('value')),
            'No Subject',
        )
        sender = next(
            (h.get('value') for h in headers if h.get('name', '').lower() == 'from' and h.get('value')),
            'Unknown Sender',
        )

        body = extract_body(payload)

        emails.append({
            'subject': subject,
            'from': sender,
            'body': body[:1000]
        })


    return emails
    


def extract_body(payload):
    """Extract plain-text content from an email, including nested MIME parts."""
    plain_text_parts = []
    html_parts = []

    def walk_parts(part):
        mime_type = part.get("mimeType", "")
        body = part.get("body") or {}
        body_data = body.get("data") if isinstance(body, dict) else None

        if mime_type == "text/plain" and body_data:
            plain_text_parts.append(body_data)
        elif mime_type == "text/html" and body_data:
            html_parts.append(body_data)

        for child in part.get("parts") or []:
            if isinstance(child, dict):
                walk_parts(child)

    if isinstance(payload, dict):
        walk_parts(payload)

    # Prefer plain text whenever the email provides it.
    encoded_parts = plain_text_parts or html_parts
    decoded_parts = []

    for data in encoded_parts:
        try:
            decoded = base64.urlsafe_b64decode(data).decode(
                "utf-8", errors="replace"
            )
            decoded_parts.append(decoded)
        except (ValueError, UnicodeError):
            continue

    return "\n".join(decoded_parts).strip()

