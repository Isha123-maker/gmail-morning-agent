# app.py
import streamlit as st
from datetime import datetime
from gmail_reader import get_todays_emails
from summarizer import summarize_emails

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
        background: radial-gradient(circle at top left, #1a1f3c 0%, #0d0f1c 45%, #0a0b14 100%);
        color: #E6E8F0;
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
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    .app-subtitle {
        font-size: 0.95rem;
        color: #9CA3AF;
        font-weight: 400;
    }

    /* Glass metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.3rem 1rem;
        text-align: center;
        transition: all 0.25s ease;
    }

    .metric-card:hover {
        border-color: rgba(127, 90, 240, 0.5);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 0.3rem;
    }

    /* Summary glass box */
    .summary-box {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.8rem;
        margin-top: 1rem;
        line-height: 1.6;
        color: #E6E8F0;
    }

    /* Email item cards */
    .email-item {
        background: rgba(255, 255, 255, 0.03);
        border-left: 3px solid #7F5AF0;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.8rem;
    }

    .email-item strong {
        color: #F0F0F5;
    }

    /* Buttons - gradient */
    .stButton>button {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        color: white;
        border-radius: 10px;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        border: none;
        transition: all 0.25s ease;
        box-shadow: 0 4px 20px rgba(127, 90, 240, 0.25);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 28px rgba(127, 90, 240, 0.4);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12142a 0%, #0a0b14 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #E6E8F0;
        font-size: 0.95rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08);
    }

    /* Slider label */
    section[data-testid="stSidebar"] label {
        color: #C4C7D4 !important;
    }

    /* Info/error boxes */
    div[data-testid="stAlert"] {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 12px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03);
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
    mark_read = st.checkbox("✅ Mark emails as read after summarizing", value=True)

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
            emails = get_todays_emails(max_emails=max_emails, mark_read=mark_read)
        except Exception as e:
            st.error(f"Gmail connection failed: {str(e)}")
            st.stop()

    with st.spinner("Generating your briefing..."):
        try:
            summary = summarize_emails(emails)
        except Exception as e:
            st.error(f"Summarization failed: {str(e)}")
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
    st.markdown(f"""<div class="summary-box">{summary}</div>""", unsafe_allow_html=True)

    # --- Raw Emails ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📨 View Individual Emails"):
        if not emails:
            st.info("No emails found for today.")
        for i, email in enumerate(emails, 1):
            st.markdown(f"""
            <div class="email-item">
                <strong>{email['subject']}</strong><br>
                <span style="color:#9CA3AF; font-size:0.82rem;">From: {email['from']}</span>
                <p style="margin-top:0.5rem; color:#C4C7D4; font-size:0.9rem;">{email['body'][:250]}...</p>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👋 Click **Generate Today's Briefing** to fetch and summarize your emails.")