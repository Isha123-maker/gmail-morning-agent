"""Standalone public Mail Brief demo; this app uses fictional messages only."""

from datetime import datetime

import streamlit as st

from demo_data import SAMPLE_EMAILS
from demo_summarizer import create_demo_briefing


st.set_page_config(
    page_title="Mail Brief Demo",
    page_icon="📬",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp {
        background: radial-gradient(circle at top left, #FBDCE2 0%, #DEDEE0 45%, #DEDEE0 100%);
        color: #333333;
    }
    header[data-testid="stHeader"] { background: transparent; }
    .app-header { padding: 1rem 0 1.1rem; margin-bottom: .5rem; }
    .app-title {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #FF9FB2, #60AB9A);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: .3rem;
    }
    .app-subtitle { font-size: .95rem; color: #60AB9A; }
    .demo-notice {
        background: rgba(251, 220, 226, .8);
        border: 1px solid rgba(255, 159, 178, .8);
        border-radius: 12px; padding: .85rem 1rem; margin: .5rem 0 1rem;
        color: #333333; font-weight: 600;
    }
    .metric-card, .summary-box, .email-item {
        background: rgba(251, 220, 226, .55);
        border: 1px solid rgba(96, 171, 154, .24);
        border-radius: 14px; padding: 1rem; margin-bottom: .8rem;
    }
    .metric-card { text-align: center; }
    .metric-value {
        font-size: 1.7rem; font-weight: 700;
        background: linear-gradient(90deg, #FF9FB2, #60AB9A);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .metric-label { color: #60AB9A; font-size: .75rem; text-transform: uppercase; }
    .email-item { border-left: 3px solid #FF9FB2; }
    .stButton>button {
        background: linear-gradient(90deg, #FF9FB2, #60AB9A); color: #333333;
        border-radius: 10px; padding: .7rem 1.8rem; font-weight: 600; border: none;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FBDCE2 0%, #DEDEE0 100%);
        color: #333333;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #333333 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="app-header">
    <div class="app-title">Mail Brief</div>
    <div class="app-subtitle">A quick look at an AI-powered inbox digest · {datetime.now().strftime('%A, %B %d, %Y')}</div>
    </div>""",
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="demo-notice">DEMO MODE — Using fictional sample emails. No real inbox is connected.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### ⚡ About this demo")
    st.caption("Try Mail Brief with fictional messages. Nothing is fetched from an inbox.")
    st.markdown("---")
    st.caption("Gemini creates the briefing when GEMINI_API_KEY is configured.")

st.markdown("### 📨 Fictional sample emails")
for email in SAMPLE_EMAILS:
    st.markdown('<div class="email-item">', unsafe_allow_html=True)
    st.markdown(f"**{email['subject']}**")
    st.caption(email["from"])
    st.write(email["body"])
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("Generate Demo Briefing", type="primary", use_container_width=True):
    with st.spinner("Preparing your demo briefing..."):
        briefing, used_gemini = create_demo_briefing(SAMPLE_EMAILS)

    if not used_gemini:
        st.info(briefing.split("\n\n", 1)[0])

    st.markdown("### 📋 Briefing")
    st.markdown(briefing, unsafe_allow_html=False)

    first, second = st.columns(2)
    with first:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(SAMPLE_EMAILS)}</div>'
            '<div class="metric-label">Fictional emails</div></div>',
            unsafe_allow_html=True,
        )
    with second:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len({email["from"] for email in SAMPLE_EMAILS})}</div>'
            '<div class="metric-label">Fictional senders</div></div>',
            unsafe_allow_html=True,
        )
