"""Unit tests for TruthLens Enterprise IAM and Cryptographic Authentication Service."""

import pytest
import time
from datetime import timedelta
from src.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    UserDatabase,
)


def test_password_hashing_and_verification():
    raw = "TruthLens@2026!"
    pwd_hash, salt = hash_password(raw)

    assert pwd_hash is not None
    assert len(pwd_hash) == 64  # sha256 hex
    assert len(salt) == 32      # 16 bytes hex

    assert verify_password(raw, pwd_hash, salt) is True
    assert verify_password("WrongPassword123!", pwd_hash, salt) is False


def test_jwt_token_creation_and_tampering():
    payload = {
        "sub": "usr_test_123",
        "email": "test@truthlens.ai",
        "role": "OFFICER",
        "clearance_level": 5
    }
    token = create_access_token(payload, expires_delta=timedelta(minutes=5))
    assert token is not None
    assert len(token.split('.')) == 3

    # Verify authentic token
    verified = verify_access_token(token)
    assert verified is not None
    assert verified["sub"] == "usr_test_123"
    assert verified["role"] == "OFFICER"
    assert verified["clearance_level"] == 5

    # Test tampering with payload
    parts = token.split('.')
    tampered_token = f"{parts[0]}.eyJyYW5kb20iOiJmYWtlIn0.{parts[2]}"
    assert verify_access_token(tampered_token) is None

    # Test expired token
    expired_token = create_access_token(payload, expires_delta=timedelta(seconds=-10))
    assert verify_access_token(expired_token) is None


def test_user_database_seeded_personas(tmp_path):
    test_db_path = str(tmp_path / "test_auth.sqlite3")
    db = UserDatabase(db_path=test_db_path)

    officer = db.get_user_by_email("officer@truthlens.ai")
    assert officer is not None
    assert officer["full_name"] == "Dr. Rhea Sen"
    assert officer["role"] == "OFFICER"
    assert officer["clearance_level"] == 5

    auth_success = db.authenticate_credentials("officer@truthlens.ai", "TruthLens@2026!")
    assert auth_success is not None
    assert auth_success["email"] == "officer@truthlens.ai"

    auth_fail = db.authenticate_credentials("officer@truthlens.ai", "WrongPass")
    assert auth_fail is None


def test_user_registration_and_duplicates(tmp_path):
    test_db_path = str(tmp_path / "test_auth.sqlite3")
    db = UserDatabase(db_path=test_db_path)

    new_user = db.create_user(
        email="auditor@ieee.org",
        password="SecureAuditPass@99!",
        full_name="Dr. Alan Turing",
        role="ACADEMIC",
        organization="IEEE Computing Society",
        clearance_level=4
    )
    assert new_user is not None
    assert new_user["email"] == "auditor@ieee.org"
    assert new_user["role"] == "ACADEMIC"

    # Duplicate registration should raise ValueError
    with pytest.raises(ValueError):
        db.create_user(
            email="auditor@ieee.org",
            password="AnotherPassword",
            full_name="Duplicate Name"
        )


def test_enterprise_sso_handshake(tmp_path):
    test_db_path = str(tmp_path / "test_auth.sqlite3")
    db = UserDatabase(db_path=test_db_path)

    # Test Google SSO
    google_user = db.authenticate_sso("google")
    assert google_user is not None
    assert "google" in google_user["sso_provider"].lower() or google_user["sso_provider"] == "google"

    # Test GitHub SSO
    github_user = db.authenticate_sso("github")
    assert github_user is not None
    assert "github" in github_user["sso_provider"].lower() or github_user["sso_provider"] == "github"

    # Test EduID SAML SSO
    eduid_user = db.authenticate_sso("eduid")
    assert eduid_user is not None

    telemetry = db.get_security_telemetry()
    assert telemetry["cipher_suite"] == "TLS_AES_256_GCM_SHA384"
    assert telemetry["total_registered_identities"] >= 5
