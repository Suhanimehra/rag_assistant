"""Unit tests for the Groq generation adapter."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from pydantic import SecretStr
from backend.services import generation


def settings():
    return SimpleNamespace(
        groq_api_key=SecretStr("test-groq-key"),
        groq_model="openai/gpt-oss-20b",
        groq_base_url="https://api.groq.com/openai/v1",
        groq_max_completion_tokens=512,
        request_timeout=10,
        enable_query_rewriting=True,
    )


class GenerationTests(unittest.TestCase):
    def test_call_model_uses_groq_chat_completions(self):
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"choices": [{"message": {"content": "Answer [S1]."}}]})
        with patch("backend.services.generation.get_settings", return_value=settings()), \
             patch("backend.services.generation.httpx.post", return_value=response) as post:
            self.assertEqual(generation.call_model("system", "user"), "Answer [S1].")
        url = post.call_args.args[0]
        kwargs = post.call_args.kwargs
        self.assertEqual(url, "https://api.groq.com/openai/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-groq-key")
        self.assertEqual(kwargs["json"]["model"], "openai/gpt-oss-20b")
        self.assertEqual(kwargs["json"]["max_completion_tokens"], 512)

    def test_empty_model_output_fails(self):
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"choices": [{"message": {"content": "   "}}]})
        with patch("backend.services.generation.get_settings", return_value=settings()), \
             patch("backend.services.generation.httpx.post", return_value=response):
            with self.assertRaises(ValueError):
                generation.call_model("system", "user")

    def test_generate_without_candidates_returns_fallback(self):
        self.assertEqual(generation.generate("question", []), generation.FALLBACK)

    def test_generate_includes_evidence_and_source_ids(self):
        candidate = SimpleNamespace(filename="doc.pdf", page=2, content="Evidence text")
        response = Mock()
        response.raise_for_status = Mock()
        response.json = Mock(return_value={"choices": [{"message": {"content": "Grounded 【S1】."}}]})
        with patch("backend.services.generation.get_settings", return_value=settings()), \
             patch("backend.services.generation.httpx.post", return_value=response) as post:
            self.assertEqual(generation.generate("What?", [candidate]), "Grounded [S1].")
        payload = json.loads(post.call_args.kwargs["json"]["messages"][1]["content"])
        self.assertEqual(payload["evidence"][0]["source"], "S1")
        self.assertEqual(payload["evidence"][0]["filename"], "doc.pdf")


if __name__ == "__main__":
    unittest.main()
