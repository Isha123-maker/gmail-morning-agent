# Mail Brief

Mail Brief has a Gmail-connected app (`app.py`) and a separate public portfolio demo (`demo_app.py`). The demo uses only fictional sample messages and does not connect to Gmail or use Gmail OAuth.

## Run the fictional demo

From this project folder, install the existing dependencies if needed, then run:

```bash
streamlit run demo_app.py
```

Gemini is optional for trying the demo. To generate a live briefing, set `GEMINI_API_KEY` in your environment or in a local `.env` file. You can start from `.env.example`, replacing its placeholder with your Gemini API key. Never commit the real key.

If the key is missing or Gemini is unavailable, the demo explains that and displays a clearly labeled sample briefing. The messages and briefing fallback are fictional.

## Run the original Gmail app

The original app remains available separately:

```bash
streamlit run app.py
```
