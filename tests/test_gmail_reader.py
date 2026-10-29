import base64
import unittest
from unittest.mock import patch
from datetime import datetime, timezone

from gmail_reader import build_today_query, extract_body, get_todays_emails


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


class MalformedPayloadTests(unittest.TestCase):
    def test_empty_or_missing_payload_returns_empty_body(self):
        self.assertEqual(extract_body(None), "")
        self.assertEqual(extract_body({}), "")

    def test_malformed_body_and_parts_are_skipped(self):
        payload = {
            "mimeType": "multipart/mixed",
            "body": None,
            "parts": [None, {"mimeType": "text/plain", "body": None},
                      {"mimeType": "text/plain", "body": {"data": "%%%"}}],
        }

        self.assertEqual(extract_body(payload), "")

    def test_invalid_utf8_is_replaced_without_failing(self):
        encoded = base64.urlsafe_b64encode(b"hello\xff").decode("ascii")
        payload = {"mimeType": "text/plain", "body": {"data": encoded}}

        self.assertEqual(extract_body(payload), "hello\ufffd")

    def test_missing_payload_and_headers_use_fallbacks(self):
        responses = [
            {"id": "missing-payload"},
            {"id": "missing-headers", "payload": {}},
            {"id": "empty-headers", "payload": {"headers": []}},
        ]
        service = _FakeGmailService(responses)
        with patch("gmail_reader.get_gmail_service", return_value=service), \
             patch("gmail_reader.build_today_query", return_value="today"):
            emails = get_todays_emails()

        self.assertEqual(emails, [
            {"subject": "No Subject", "from": "Unknown Sender", "body": ""},
            {"subject": "No Subject", "from": "Unknown Sender", "body": ""},
            {"subject": "No Subject", "from": "Unknown Sender", "body": ""},
        ])

    def test_missing_subject_and_from_use_fallbacks(self):
        service = _FakeGmailService([{
            "id": "partial-headers",
            "payload": {"headers": [{"name": "Subject"}, {"name": "From", "value": ""}]},
        }])
        with patch("gmail_reader.get_gmail_service", return_value=service), \
             patch("gmail_reader.build_today_query", return_value="today"):
            emails = get_todays_emails()

        self.assertEqual(emails[0]["subject"], "No Subject")
        self.assertEqual(emails[0]["from"], "Unknown Sender")


class _FakeRequest:
    def __init__(self, value):
        self.value = value

    def execute(self):
        return self.value


class _FakeMessages:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def list(self, **kwargs):
        return _FakeRequest({"messages": [{"id": str(i)} for i in range(len(self.responses))]})

    def get(self, **kwargs):
        value = self.responses[self.index]
        self.index += 1
        return _FakeRequest(value)


class _FakeUsers:
    def __init__(self, responses):
        self._messages = _FakeMessages(responses)

    def messages(self):
        return self._messages


class _FakeGmailService:
    def __init__(self, responses):
        self._users = _FakeUsers(responses)

    def users(self):
        return self._users


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
