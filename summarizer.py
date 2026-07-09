# summarizer.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

def summarize_emails(emails: list) -> str:
    """
    Takes a list of emails and returns a clean summary.
    Think of this as handing a pile of letters to a very smart assistant
    and saying 'give me the highlights'.
    """

    if not emails:
        return "📭 No emails found for today! Inbox zero — you're winning!"

    # Initialize Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # Free and fast!
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3  # Lower = more focused, less creative
    )

    # Format all emails into one big text block
    email_text = ""
    for i, email in enumerate(emails, 1):
        email_text += f"""
--- Email {i} ---
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}
"""

    # The prompt — this is where the magic instruction lives
    messages = [
        SystemMessage(content="""You are a professional email assistant.
        Your job is to read emails and give a clear, concise morning briefing.
        Be friendly, organized, and highlight anything urgent."""),

        HumanMessage(content=f"""
        Here are today's emails. Please provide:

        1. 📊 QUICK STATS: How many emails total, how many seem urgent
        2. 🔴 URGENT/ACTION REQUIRED: Emails needing immediate response
        3. 📋 SUMMARY BY EMAIL: One-line summary for each email
        4. 💡 KEY TAKEAWAYS: 2-3 most important things to know today

        Emails:
        {email_text}
        """)
    ]

    response = llm.invoke(messages)
    return response.content