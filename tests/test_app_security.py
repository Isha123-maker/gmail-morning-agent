
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class AppSecurityTests(unittest.TestCase):
    def test_email_content_and_summary_with_html_payloads(self):
        malicious_content = (
            '<script>alert("xss")</script>'
            '<img src=x onerror=alert(1)>'
        )
        malicious_summary = (
            'Summary text <script>alert("xss")</script>'
        )

        with (
            patch("gmail_reader.get_todays_emails", return_value=[
                {
                    "subject": malicious_content,
                    "from": "sender@example.com",
                    "body": malicious_content,
                }
            ]),
            patch(
                "summarizer.summarize_emails",
                return_value=malicious_summary,
            ),
        ):
            project_root = Path(__file__).resolve().parent.parent
            app = AppTest.from_file(
                str(project_root / "app.py"),
                default_timeout=10,
            )
            app.run()
            app.button[0].click().run()

        self.assertFalse(app.exception)

        # Email fields and body preview should use plain-text elements.
        rendered_text = [element.value for element in app.text]
        self.assertTrue(
            any(malicious_content in value for value in rendered_text),
            "Malicious email content should remain in plain-text output.",
        )

        # The summary should be displayed through Markdown, not unsafe HTML.
        rendered_markdown = [element.value for element in app.markdown]
        self.assertTrue(
            any(malicious_summary in value for value in rendered_markdown),
            "The AI summary should still appear in the briefing.",
        )


if __name__ == "__main__":
    unittest.main()
