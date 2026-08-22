"""Entry point for uvicorn: uvicorn app:app --reload"""

from app.main import app

__all__ = ["app"]
