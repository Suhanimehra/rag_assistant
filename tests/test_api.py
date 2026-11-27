"""API integration tests using a temporary SQLite metadata DB and mocked retrieval."""
import os
import unittest
from unittest.mock import patch
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from backend.database import Base, get_db
from backend.config import get_settings
from backend.main import app
from backend.security import (chat_limiter, login_ip_limiter, login_limiter, register_ip_limiter,
                               register_limiter, SlidingWindowLimiter)
from backend.services.ranking import Candidate

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.settings = patch.dict(os.environ, {
            "DATABASE_URL":"sqlite://",
            "JWT_SECRET":"test-only-secret-do-not-use-in-production-123",
            "GROQ_API_KEY":"test-only-groq-key",
        })
        self.settings.start()
        get_settings.cache_clear()
        login_limiter.reset()
        login_ip_limiter.reset()
        register_limiter.reset()
        register_ip_limiter.reset()
        chat_limiter.reset()
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.factory = sessionmaker(bind=self.engine)
        def db():
            with self.factory() as session:
                yield session
        app.dependency_overrides[get_db] = db
        self.client = TestClient(app)
        result = self.client.post("/register", json={"username":"Test","email":"test@example.com","password":"long-test-password"})
        self.assertEqual(result.status_code, 201)
        result = self.client.post("/login", data={"username":"test@example.com","password":"long-test-password"})
        self.assertEqual(result.status_code, 200)
        self.headers = {"Authorization":"Bearer "+result.json()["access_token"]}

    def tearDown(self):
        app.dependency_overrides.clear()
        self.engine.dispose()
        self.settings.stop()
        get_settings.cache_clear()
        login_limiter.reset()
        login_ip_limiter.reset()
        register_limiter.reset()
        register_ip_limiter.reset()
        chat_limiter.reset()

    def test_conversation_round_trip(self):
        chat = self.client.post("/conversations/start", headers=self.headers).json()
        candidate = Candidate(1, 1, "example.pdf", 2, "Python supports decorators.", .8)
        with patch("backend.api.conversations.retrieve", return_value=[candidate]), patch("backend.api.conversations.generate", return_value="Python supports decorators [S1]."):
            result = self.client.post("/conversations/chat", headers=self.headers, json={"conversation_id":chat["conversation_id"],"question":"What does Python support?"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["sources"][0]["page"], 2)
        history = self.client.get(f"/conversations/messages/{chat['conversation_id']}", headers=self.headers).json()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[1]["sources"][0]["filename"], "example.pdf")

    def test_user_registration_role(self):
        from backend.models import User
        with self.factory() as db:
            user = db.query(User).first()
            self.assertEqual(user.role, "user")
            self.assertNotEqual(user.password, "long-test-password")
            self.assertEqual(user.token_version, 0)
        self.assertEqual(self.client.get("/documents", headers=self.headers).status_code, 200)

    def test_chat_listing(self):
        self.assertEqual(self.client.post("/conversations/start", headers=self.headers).status_code, 201)
        self.assertEqual(len(self.client.get("/conversations/list", headers=self.headers).json()), 1)

    def test_logout_revokes_existing_token(self):
        self.assertEqual(self.client.post("/logout", headers=self.headers).status_code, 200)
        self.assertEqual(self.client.get("/conversations/list", headers=self.headers).status_code, 401)

    def test_security_headers(self):
        response = self.client.get("/conversations/list", headers=self.headers)
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertEqual(response.headers["cache-control"], "no-store")

    def test_blank_inputs_are_rejected(self):
        response = self.client.post("/register", json={"username":"   ","email":"blank@example.com","password":"long-test-password"})
        self.assertEqual(response.status_code, 422)
        chat = self.client.post("/conversations/start", headers=self.headers).json()
        response = self.client.post("/conversations/chat", headers=self.headers,
                                    json={"conversation_id":chat["conversation_id"],"question":"   "})
        self.assertEqual(response.status_code, 422)

    def test_failed_generation_keeps_user_question(self):
        chat = self.client.post("/conversations/start", headers=self.headers).json()
        with patch("backend.api.conversations.retrieve", return_value=[]), \
             patch("backend.api.conversations.generate", side_effect=httpx.HTTPError("unavailable")):
            response = self.client.post("/conversations/chat", headers=self.headers,
                                        json={"conversation_id":chat["conversation_id"],"question":"Will this persist?"})
        self.assertEqual(response.status_code, 503)
        history = self.client.get(f"/conversations/messages/{chat['conversation_id']}", headers=self.headers).json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["message"], "Will this persist?")

    def test_login_rate_limit(self):
        with patch("backend.api.auth.login_limiter", SlidingWindowLimiter(limit=1, window_seconds=60)):
            self.assertEqual(self.client.post("/login", data={"username":"test@example.com","password":"wrong-password"}).status_code, 401)
            response = self.client.post("/login", data={"username":"test@example.com","password":"wrong-password"})
        self.assertEqual(response.status_code, 429)
        self.assertIn("retry-after", response.headers)
