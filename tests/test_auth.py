import pytest
import os
from unittest.mock import patch
from src.integrations.google_auth import GoogleAuth

def test_google_auth_init():
    auth = GoogleAuth()
    assert auth is not None

def test_creds_check_no_file():
    auth = GoogleAuth()
    with patch("os.path.exists", return_value=False):
        if hasattr(auth, 'get_credentials'):
            creds = auth.get_credentials()
            assert creds is None

def test_google_auth_methods():
    from src.integrations.google_auth import GoogleAuth
    auth = GoogleAuth()
    assert hasattr(auth, 'get_service')
    assert hasattr(auth, '_refresh_or_auth')
    