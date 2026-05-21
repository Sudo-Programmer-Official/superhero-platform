from fastapi import HTTPException

from app.auth.dependencies import _extract_bearer


def test_extract_bearer_missing_header() -> None:
    try:
        _extract_bearer(None)
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401


def test_extract_bearer_invalid_scheme() -> None:
    try:
        _extract_bearer("Basic abc")
        assert False, "expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401


def test_extract_bearer_valid_token() -> None:
    token = _extract_bearer("Bearer token-123")
    assert token == "token-123"
