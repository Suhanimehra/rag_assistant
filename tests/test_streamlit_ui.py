"""UI smoke tests using mocked V2 API responses; no database or Ollama required."""
import unittest
from unittest.mock import patch
from pathlib import Path

from streamlit.testing.v1 import AppTest


class Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status_code = status

    def json(self):
        return self.payload


class StreamlitTests(unittest.TestCase):
    def setUp(self):
        self.chats = []
        self.messages = []
        self.client = patch("requests.request", side_effect=self.request)
        self.client.start()
        self.addCleanup(self.client.stop)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "streamlit_app.py"))

    def request(self, method, url, **kwargs):
        path = url.split(":8000", 1)[-1]
        if path == "/login":
            return Response({"access_token": "mock-token", "role": "admin"})
        if path == "/conversations/list":
            return Response(self.chats)
        if path == "/conversations/start":
            self.chats.append({"id": 1, "title": "New Chat"})
            return Response({"conversation_id": 1, "title": "New Chat"}, 201)
        if path == "/documents":
            return Response([{"id": 2, "filename": "sample.pdf"}])
        if path == "/ingest/jobs":
            return Response([{"job_id": 3, "filename": "sample.pdf", "status": "completed", "chunks_stored": 5}])
        if path == "/conversations/messages/1":
            return Response(self.messages)
        if path == "/conversations/chat":
            source = {"source_id": "S1", "filename": "sample.pdf", "page": 1, "excerpt": "Sample evidence."}
            self.messages.extend([{"role": "user", "message": kwargs["json"]["question"]},
                                  {"role": "assistant", "message": "Sample answer [S1]", "sources": [source]}])
            return Response({"answer": "Sample answer [S1]", "sources": [source],
                             "retrieval_ms": 20, "generation_ms": 200, "insufficient_evidence": False})
        if path in ("/health", "/system/status"):
            return Response({
                "status": "healthy",
                "database": "connected"
        })
        raise AssertionError((method, path))

    def login(self):
        self.app.run()
        self.app.text_input[0].set_value("test@example.com")
        self.app.text_input[1].set_value("example-password")
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)

    def test_chat_round_trip(self):
        self.login()
        next(b for b in self.app.button if "New conversation" in b.label).click().run()
        self.assertFalse(self.app.exception)
        self.app.chat_input[0].set_value("What is this document about?").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.chat_message), 2)

    def test_documents_and_system(self):
        self.login()
        next(button for button in self.app.button if "Documents" in button.label).click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.dataframe), 2)
        next(button for button in self.app.button if "System" in button.label).click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.metric), 2)

if __name__ == "__main__":
    unittest.main()
