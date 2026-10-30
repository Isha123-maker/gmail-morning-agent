# Mail Brief

Mail Brief is a local Streamlit app that fetches today’s Gmail messages and uses Google Gemini to create a concise morning briefing.

## Features

- Reads messages from the current day in Pakistan time.
- Requests Gmail read-only access.
- Summarizes messages with Gemini (`gemini-2.5-flash`).
- Shows a briefing and individual email previews in a Streamlit interface.
- Handles missing email fields and nested MIME message parts.

## Requirements

- Python 3.12
- A Google Cloud OAuth client configured for the Gmail API
- A Gemini API key

## Setup

1. Clone the repository and open its folder:

   ```powershell
   git clone https://github.com/Isha123-maker/gmail-morning-agent.git
   cd gmail-morning-agent
   ```

2. Create and activate a virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install the pinned dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Create a `.env` file in the project folder with your Gemini API key:

   ```dotenv
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. Configure Gmail OAuth:

   - Enable the Gmail API in your Google Cloud project.
   - Create an OAuth client for a desktop application.
   - Download its client credentials file into the project folder as `credentials.json`.
   - Add your Google account as a test user if your OAuth app is in testing mode.

   The app requests this scope:

   ```text
   https://www.googleapis.com/auth/gmail.readonly
   ```

   On first launch, a browser window opens for Google authorization. After successful authorization, a local `token.json` file is created for later runs.

## Run the app

From the project folder, with the virtual environment active:

```powershell
streamlit run app.py
```

Choose **Generate Today's Briefing** to fetch today’s messages and create the briefing.

## Run tests

Run the full test suite:

```powershell
python -m unittest discover -s tests -v
```

The tests cover Gmail message parsing, timezone-aware date queries, safe rendering of email and summary content, missing Gmail credentials, and missing Gemini key validation.

## Local files and secrets

Keep these files private and out of version control:

- `.env`
- `credentials.json`
- `token.json`

The repository’s `.gitignore` is configured to exclude these files. Never commit or share their contents. If an OAuth token must be reset, stop the app and remove `token.json`; the next run will ask you to authorize again.

## Current scope

This version is intended for local use with one Gmail account. It does not implement per-user OAuth or encrypted multi-user token storage. It is not yet configured as a public service.