"""Gemini briefing support for fictional demo messages only."""

from demo_data import SAMPLE_BRIEFING
from summarizer import summarize_emails


def create_demo_briefing(emails: list[dict]) -> tuple[str, bool]:
    """Return a Gemini briefing or a labeled fallback when Gemini is unavailable."""
    try:
        return summarize_emails(emails), True
    except Exception:
        return (
            "Gemini is unavailable right now, so here is a sample briefing "
            "using the fictional messages below.\n\n" + SAMPLE_BRIEFING,
            False,
        )
