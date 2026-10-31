"""Direct unit tests for TruthLens Enterprise IAM API endpoints."""

import pytest
import secrets
from fastapi import HTTPException
from src.api.server import (
    auth_telemetry,
    auth_login,
    auth_register,
    auth_sso,
    auth_me,
    auth_logout,
    LoginRequest,
    RegisterRequest,
    SSORequest,
)


def test_auth_telemetry_endpoint():
    data = auth_telemetry()
    assert data["cipher_suite"] == "TLS_AES_256_GCM_SHA384"
    assert data["total_registered_identities"] >= 5
    assert "IFCN Section 2 (Transparency)" in data["compliance_standards"]


def test_auth_login_and_me_flow():
    # Valid login
    login_req = LoginRequest(email="officer@truthlens.ai", password="TruthLens@2026!")
    login_res = auth_login(login_req)
    assert login_res["status"] == "authenticated"
    assert "token" in login_res
    token = login_res["token"]
    assert login_res["user"]["role"] == "OFFICER"

    # Authenticated /me endpoint
    me_res = auth_me(authorization=f"Bearer {token}")
    assert me_res["user"]["email"] == "officer@truthlens.ai"
    assert me_res["claims"]["role"] == "OFFICER"

    # Invalid login
    bad_req = LoginRequest(email="officer@truthlens.ai", password="WrongPassword")
    with pytest.raises(HTTPException) as exc:
        auth_login(bad_req)
    assert exc.value.status_code == 401


def test_auth_sso_endpoint():
    res = auth_sso("google")
    assert res["status"] == "sso_authenticated"
    assert res["provider"] == "google"
    assert "token" in res


def test_auth_register_endpoint():
    unique_email = f"investigator.{secrets.token_hex(4)}@reuters.com"
    reg_req = RegisterRequest(
        email=unique_email,
        password="ValidPassword@99!",
        full_name="Lead Investigator Alpha",
        role="JOURNALIST",
        organization="Reuters Investigations",
        clearance_level=4
    )
    res = auth_register(reg_req)
    assert res["status"] == "registered"
    assert res["user"]["email"] == unique_email

    # Duplicate should raise 400
    with pytest.raises(HTTPException) as exc:
        auth_register(reg_req)
    assert exc.value.status_code == 400


def test_auth_logout_endpoint():
    res = auth_logout()
    assert res["status"] == "logged_out"
