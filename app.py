# app.py
import streamlit as st
from datetime import datetime
from gmail_reader import get_todays_emails
from summarizer import summarize_emails

# --- Page Config ---
st.set_page_config(
    page_title="📧 Gmail Morning Briefing",
    page_icon="📧",
    layout="centered"
)

# --- Header ---
st.title("📧 Gmail Morning Briefing Agent")
st.markdown(f"*Good morning! Today is **{datetime.now().strftime('%A, %B %d %Y')}***")
st.divider()

# --- Sidebar Settings ---
with st.sidebar:
    st.header("⚙️ Settings")
    max_emails = st.slider("Max emails to fetch", 5, 50, 20)
    st.info("💡 First time? Click the button below and log into your Gmail when the browser opens!")

# --- Main Button ---
if st.button("🚀 Fetch & Summarize My Emails", type="primary", use_container_width=True):

    with st.spinner("📬 Fetching your emails..."):
        try:
            emails = get_todays_emails(max_emails=max_emails)
            st.success(f"✅ Found {len(emails)} emails today!")
        except Exception as e:
            st.error(f"❌ Gmail connection failed: {str(e)}")
            st.stop()

    with st.spinner("🧠 Gemini is reading and summarizing..."):
        try:
            summary = summarize_emails(emails)
        except Exception as e:
            st.error(f"❌ Summarization failed: {str(e)}")
            st.stop()

    # --- Display Summary ---
    st.divider()
    st.subheader("📋 Your Morning Email Summary")
    st.markdown(summary)

    # --- Show Raw Emails (Optional Expander) ---
    with st.expander("📨 See raw emails fetched"):
        for i, email in enumerate(emails, 1):
            st.markdown(f"**{i}. {email['subject']}**")
            st.caption(f"From: {email['from']}")
            st.text(email['body'][:300] + "...")
            st.divider()