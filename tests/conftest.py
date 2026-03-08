"""Pytest fixtures for pocket-tts-server."""
import sys
from pathlib import Path

# Add project root so "pocket_tts_api" and "wyoming_protocol" are importable
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pytest

# Lazy imports so tests that don't need the app (e.g. test_wyoming) can run
# without installing FastAPI / full server deps.
_app = None


def _get_app():
    global _app
    if _app is None:
        from pocket_tts_api import app as _app_inner

        _app = _app_inner
    return _app


@pytest.fixture
def client():
    """FastAPI TestClient. Triggers lifespan on first request."""
    from fastapi.testclient import TestClient

    return TestClient(_get_app())
