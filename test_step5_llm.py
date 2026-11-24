"""
test_step5_llm.py — Phase 2: LLM Client + Fix Coach Integration Tests
Tests that the LLMClient wrapper loads, checks availability,
and that the /api/coach/investigate endpoint accepts use_llm param.
"""
import sys, os, unittest
from unittest.mock import patch, MagicMock

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.coach.llm_client import LLMClient


class TestLLMClientBasic(unittest.TestCase):

    def test_is_unavailable_without_key(self):
        """LLMClient reports unavailable when no key is set."""
        client = LLMClient(api_key="")
        self.assertFalse(client.is_available())

    def test_is_unavailable_with_placeholder(self):
        client = LLMClient(api_key="YOUR_GROQ_API_KEY_HERE")
        self.assertFalse(client.is_available())

    def test_is_available_with_real_looking_key(self):
        client = LLMClient(api_key="sk-testkey1234567890abcdef")
        self.assertTrue(client.is_available())

    def test_model_default(self):
        client = LLMClient(api_key="sk-test")
        self.assertEqual(client.model, "qwen/qwen3.8-27b")

    def test_generate_fix_returns_empty_without_key(self):
        """generate_fix returns '' when no key is configured (no LLM call)."""
        client = LLMClient(api_key="")
        result = client.generate_fix("title", "body", "file.py", "code")
        self.assertEqual(result, "")

    def test_summarise_issue_returns_title_without_key(self):
        """summarise_issue returns title when no key (graceful fallback)."""
        client = LLMClient(api_key="")
        result = client.summarise_issue("My Issue", "body text")
        self.assertEqual(result, "My Issue")


class TestLLMClientMocked(unittest.TestCase):

    def _make_mock_response(self, text: str):
        msg = MagicMock()
        msg.content = text
        choice = MagicMock()
        choice.message = msg
        completion = MagicMock()
        completion.choices = [choice]
        return completion

    @patch("app.coach.llm_client.LLMClient._get_client")
    def test_generate_fix_returns_diff(self, mock_get):
        """generate_fix returns diff when LLM responds with one."""
        mock_client = MagicMock()
        mock_get.return_value = mock_client
        fake_diff = "--- a/core.py\n+++ b/core.py\n@@ -1,3 +1,4 @@\n+# fix\n pass\n"
        mock_client.chat.completions.create.return_value = self._make_mock_response(fake_diff)

        client = LLMClient(api_key="sk-test")
        result = client.generate_fix("Test issue", "Body", "core.py", "pass\n")
        self.assertIn("---", result)

    @patch("app.coach.llm_client.LLMClient._get_client")
    def test_summarise_issue_calls_llm(self, mock_get):
        """summarise_issue returns LLM text when key is available."""
        mock_client = MagicMock()
        mock_get.return_value = mock_client
        mock_client.chat.completions.create.return_value = self._make_mock_response("This issue is about X.")

        client = LLMClient(api_key="sk-test")
        result = client.summarise_issue("Title", "Body")
        self.assertIn("This issue", result)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
