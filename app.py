# app.py
import logging

import streamlit as st
from datetime import datetime
from gmail_reader import get_todays_emails
from summarizer import summarize_emails

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# --- Page Config ---
st.set_page_config(
    page_title="Mail Brief",
    page_icon="📬",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Custom CSS: Dark Modern Gradient Theme ---
st.markdown("""
<style>
    /* Import a clean modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* App background - deep gradient */
    .stApp {
        background: radial-gradient(circle at top left, #FBDCE2 0%, #DEDEE0 45%, #DEDEE0 100%);
        color: #333333;
    }

    /* Hide default header decoration */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Header block */
    .app-header {
        padding: 1rem 0 1.5rem 0;
        margin-bottom: 1rem;
    }

    .app-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF9FB2, #60AB9A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: #60AB9A;
        font-weight: 400;
    }

    /* Glass metric cards */
    .metric-card {
        background: rgba(251, 220, 226, 0.55);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(96, 171, 154, 0.24);
        border-radius: 14px;
        padding: 1.3rem 1rem;
        text-align: center;
        transition: all 0.25s ease;
    }

    .metric-card:hover {
        border-color: rgba(255, 159, 178, 0.8);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF9FB2, #60AB9A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #60AB9A;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 0.3rem;
    }

    /* Summary glass box */
    .summary-box {
        background: rgba(251, 220, 226, 0.55);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(96, 171, 154, 0.24);
        border-radius: 16px;
        padding: 1.8rem;
        margin-top: 1rem;
        line-height: 1.6;
        color: #333333;
    }

    /* Email item cards */
    .email-item {
        background: rgba(251, 220, 226, 0.55);
        border-left: 3px solid #FF9FB2;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.8rem;
    }

    .email-item strong {
        color: #333333;
    }

    /* Buttons - gradient */
    .stButton>button {
        background: linear-gradient(90deg, #FF9FB2, #60AB9A);
        color: #333333;
        border-radius: 10px;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        border: none;
        transition: all 0.25s ease;
        box-shadow: 0 4px 20px rgba(96, 171, 154, 0.25);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 28px rgba(96, 171, 154, 0.4);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FBDCE2 0%, #DEDEE0 100%);
        border-right: 1px solid rgba(96, 171, 154, 0.24);
        color: #333333;
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #333333 !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #333333;
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(96, 171, 154, 0.24);
    }

    /* Slider label */
    section[data-testid="stSidebar"] label {
        color: #333333 !important;
    }

    /* Info/error boxes */
    div[data-testid="stAlert"] {
        background: rgba(251, 220, 226, 0.55);
        border-radius: 12px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(251, 220, 226, 0.55);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown(f"""
<div class="app-header">
    <div class="app-title">Mail Brief</div>
    <div class="app-subtitle">Your AI-powered inbox digest — {datetime.now().strftime('%A, %B %d, %Y')}</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ⚡ Settings")
    max_emails = st.slider("Max emails to fetch", 5, 50, 20)

    st.markdown("---")
    st.markdown("### 🧠 How It Works")
    st.caption("Mail Brief securely connects to Gmail, pulls today's messages, and uses Google Gemini to generate a concise executive briefing.")

    st.markdown("---")
    st.markdown("### 🛠️ Stack")
    st.caption("LangChain · Gemini API · Gmail API · Streamlit")

    st.markdown("---")
    st.caption("Built by Noor 👩‍💻")

# --- Main Action ---
fetch_clicked = st.button("Generate Today's Briefing", type="primary", use_container_width=True)

if fetch_clicked:

    with st.spinner("Connecting to Gmail..."):
        try:
            emails = get_todays_emails(max_emails=max_emails)
        except Exception:
           logger.exception("Failed to fetch emails from Gmail")
           st.error(
             "We couldn't connect to Gmail or fetch your  emails. "
             "Please check your connection and Gmail authorization, then try again."
            )
           st.stop()
        
    if not emails:
        st.info("📭 No emails found for today. You're all caught up!")
        st.stop()

    with st.spinner("Generating your briefing..."):
        try:
            summary = summarize_emails(emails)
        except Exception:
            logger.exception("Failed to generate the email summary")
            st.error(
               "We couldn't generate your briefing. "
               "Please check your Gemini API configuration and try again."
           )
            st.stop()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Metrics Row ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(emails)}</div>
            <div class="metric-label">Emails Today</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        senders = len(set(e['from'] for e in emails)) if emails else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{senders}</div>
            <div class="metric-label">Senders</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{datetime.now().strftime('%I:%M %p')}</div>
            <div class="metric-label">Generated</div>
        </div>
        """, unsafe_allow_html=True)

    # --- Summary Section ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 Briefing")
    with st.container(border=True):
        st.markdown(summary, unsafe_allow_html=False)

    # --- Raw Emails ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📨 View Individual Emails"):
        if not emails:
            st.info("No emails found for today.")
        for i, email in enumerate(emails, 1):
           with st.container(border=True):
              st.caption(f"Email {i}")
              st.text(f"Subject: {email.get('subject', '(No subject)')}")
              st.text(f"From: {email.get('from', 'Unknown sender')}")

              body = email.get("body") or ""
              preview = body[:250]
              if len(body) > 250:
                  preview += "..."

              st.text(preview)

else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👋 Click **Generate Today's Briefing** to fetch and summarize your emails.")
