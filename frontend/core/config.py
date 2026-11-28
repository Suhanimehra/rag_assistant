"""Static configuration."""
import os

API = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")
ALLOWED_UPLOADS = ["pdf", "txt", "md", "csv"]
