import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from demo_data import SAMPLE_BRIEFING, SAMPLE_EMAILS
from demo_summarizer import create_demo_briefing


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DemoAppTests(unittest.TestCase):
    def test_demo_never_imports_or_calls_gmail_code(self):
        for filename in ("demo_app.py", "demo_summarizer.py", "demo_data.py"):
            tree = ast.parse((PROJECT_ROOT / filename).read_text(encoding="utf-8"))
            imported = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imported.update(
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            )
            self.assertNotIn("gmail_reader", imported, filename)

    def test_demo_uses_visible_notice_and_fictional_emails(self):
        source = (PROJECT_ROOT / "demo_app.py").read_text(encoding="utf-8")
        self.assertIn("DEMO MODE — Using fictional sample emails. No real inbox is connected.", source)
        self.assertIn("Fictional sample emails", source)
        self.assertEqual(len(SAMPLE_EMAILS), 3)
        self.assertTrue(all(email["from"].endswith("example.test>") for email in SAMPLE_EMAILS))

    def test_missing_or_failed_gemini_shows_sample_fallback(self):
        with patch("demo_summarizer.summarize_emails", side_effect=ValueError("missing key")):
            briefing, used_gemini = create_demo_briefing(SAMPLE_EMAILS)

        self.assertFalse(used_gemini)
        self.assertIn("Gemini is unavailable right now", briefing)
        self.assertIn("Sample briefing", briefing)
        self.assertIn("fictional project", briefing.lower())
        self.assertIn(SAMPLE_BRIEFING, briefing)

    def test_demo_uses_gemini_result_when_available(self):
        with patch("demo_summarizer.summarize_emails", return_value="Gemini demo summary") as summarize:
            briefing, used_gemini = create_demo_briefing(SAMPLE_EMAILS)

        summarize.assert_called_once_with(SAMPLE_EMAILS)
        self.assertTrue(used_gemini)
        self.assertEqual(briefing, "Gemini demo summary")


if __name__ == "__main__":
    unittest.main()
