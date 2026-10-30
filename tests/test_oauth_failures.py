import unittest
from unittest.mock import patch

from gmail_reader import get_gmail_service


class OAuthFailureTests(unittest.TestCase):
    @patch("summarizer.os.getenv", return_value=None)
    def test_missing_gemini_key_is_rejected(self, _mock_getenv):
        from summarizer import validate_config

        with self.assertRaisesRegex(
            ValueError,
            "GEMINI_API_KEY is missing or still uses the example placeholder",
        ):
            validate_config()

    @patch("gmail_reader.st.secrets", {})
    @patch("gmail_reader.os.path.exists", return_value=False)
    @patch("gmail_reader.InstalledAppFlow.from_client_secrets_file")
    def test_missing_credentials_file_is_reported(
        self, mock_flow, _mock_exists
    ):
        mock_flow.side_effect = FileNotFoundError("credentials.json is missing")

        with self.assertRaisesRegex(FileNotFoundError, "credentials.json"):
            get_gmail_service()

        mock_flow.assert_called_once()


if __name__ == "__main__":
    unittest.main()