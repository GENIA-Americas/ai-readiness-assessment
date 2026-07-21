import os

os.environ["DATABASE_URL"] = "sqlite:///./test_readiness.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "org_name": "Acme Test Co",
    "sector": "Manufacturing",
    "org_size": "51-200",
    "responses": {
        "data_centralized": 4,
        "data_quality_process": 3,
        "ai_literate_staff": 2,
        "dedicated_owner": 3,
        "has_ai_policy": 1,
        "risk_review_process": 2,
        "cloud_or_api_access": 4,
        "integration_capacity": 3,
        "leadership_buy_in": 4,
        "budget_allocated": 3,
    },
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_assessment():
    resp = client.post("/assessments", json=VALID_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert body["org_name"] == "Acme Test Co"
    assert "overall_score" in body
    assert body["readiness_tier"] in {
        "AI-Ready",
        "Emerging",
        "Foundational",
        "Not Yet Ready",
    }


def test_get_assessment():
    create_resp = client.post("/assessments", json=VALID_PAYLOAD)
    assessment_id = create_resp.json()["id"]

    resp = client.get(f"/assessments/{assessment_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == assessment_id


def test_get_missing_assessment_returns_404():
    resp = client.get("/assessments/999999")
    assert resp.status_code == 404


def test_list_assessments():
    client.post("/assessments", json=VALID_PAYLOAD)
    resp = client.get("/assessments")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_rejects_out_of_range_score():
    bad_payload = {**VALID_PAYLOAD, "responses": {**VALID_PAYLOAD["responses"], "data_centralized": 9}}
    resp = client.post("/assessments", json=bad_payload)
    assert resp.status_code == 422


def test_rejects_unknown_field():
    bad_payload = {**VALID_PAYLOAD, "unexpected_field": "nope"}
    resp = client.post("/assessments", json=bad_payload)
    assert resp.status_code == 422
