import base64
import unittest
from datetime import datetime, timezone

from gmail_reader import build_today_query, extract_body


def gmail_data(text):
    """Encode sample text the way Gmail's URL-safe body.data is represented."""
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("ascii")


class ExtractBodyTests(unittest.TestCase):
    def test_prefers_plain_text_in_nested_multipart_payload(self):
        payload = {
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "multipart/alternative",
                    "parts": [
                        {"mimeType": "text/plain", "body": {"data": gmail_data("Hello from plain text.")}},
                        {"mimeType": "text/html", "body": {"data": gmail_data("<p>Hello from HTML.</p>")}},
                    ],
                }
            ],
        }

        self.assertEqual(extract_body(payload), "Hello from plain text.")

    def test_uses_html_when_no_plain_text_is_available(self):
        payload = {
            "mimeType": "text/html",
            "body": {"data": gmail_data("<p>HTML only.</p>")},
        }

        self.assertEqual(extract_body(payload), "<p>HTML only.</p>")


class TodayQueryTests(unittest.TestCase):
    def test_uses_pakistan_calendar_day_when_utc_date_is_different(self):
        # 20:00 UTC on Jan 1 is 01:00 on Jan 2 in Karachi.
        now = datetime(2025, 1, 1, 20, 0, tzinfo=timezone.utc)

        self.assertEqual(
            build_today_query(now),
            "after:1735758000 before:1735844400",
        )

    def test_rejects_naive_datetime(self):
        with self.assertRaises(ValueError):
            build_today_query(datetime(2025, 1, 2, 1, 0))


if __name__ == "__main__":
    unittest.main()
