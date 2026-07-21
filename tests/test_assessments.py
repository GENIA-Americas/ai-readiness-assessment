import os

os.environ["DATABASE_URL"] = "sqlite:///./test_readiness.db"
os.environ["API_KEYS"] = "devkey1:acme_corp,devkey2:globex_inc"

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ACME_HEADERS = {"X-API-Key": "devkey1"}
GLOBEX_HEADERS = {"X-API-Key": "devkey2"}

VALID_PAYLOAD = {
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


def test_create_assessment_requires_api_key():
    resp = client.post("/assessments", json=VALID_PAYLOAD)
    assert resp.status_code == 401


def test_create_assessment():
    resp = client.post("/assessments", json=VALID_PAYLOAD, headers=ACME_HEADERS)
    assert resp.status_code == 201
    body = resp.json()
    assert body["org_name"] == "acme_corp"
    assert "overall_score" in body
    assert body["readiness_tier"] in {
        "AI-Ready",
        "Emerging",
        "Foundational",
        "Not Yet Ready",
    }


def test_get_assessment():
    create_resp = client.post("/assessments", json=VALID_PAYLOAD, headers=ACME_HEADERS)
    assessment_id = create_resp.json()["id"]

    resp = client.get(f"/assessments/{assessment_id}", headers=ACME_HEADERS)
    assert resp.status_code == 200
    assert resp.json()["id"] == assessment_id


def test_cannot_read_another_orgs_assessment():
    create_resp = client.post("/assessments", json=VALID_PAYLOAD, headers=ACME_HEADERS)
    assessment_id = create_resp.json()["id"]

    resp = client.get(f"/assessments/{assessment_id}", headers=GLOBEX_HEADERS)
    assert resp.status_code == 404


def test_get_missing_assessment_returns_404():
    resp = client.get("/assessments/999999", headers=ACME_HEADERS)
    assert resp.status_code == 404


def test_list_assessments_requires_api_key():
    resp = client.get("/assessments")
    assert resp.status_code == 401


def test_list_assessments_only_returns_own_org():
    client.post("/assessments", json=VALID_PAYLOAD, headers=ACME_HEADERS)
    client.post("/assessments", json=VALID_PAYLOAD, headers=GLOBEX_HEADERS)

    acme_list = client.get("/assessments", headers=ACME_HEADERS).json()
    assert all(item["org_name"] == "acme_corp" for item in acme_list)

    globex_list = client.get("/assessments", headers=GLOBEX_HEADERS).json()
    assert all(item["org_name"] == "globex_inc" for item in globex_list)


def test_rejects_out_of_range_score():
    bad_payload = {**VALID_PAYLOAD, "responses": {**VALID_PAYLOAD["responses"], "data_centralized": 9}}
    resp = client.post("/assessments", json=bad_payload, headers=ACME_HEADERS)
    assert resp.status_code == 422


def test_rejects_unknown_field():
    bad_payload = {**VALID_PAYLOAD, "unexpected_field": "nope"}
    resp = client.post("/assessments", json=bad_payload, headers=ACME_HEADERS)
    assert resp.status_code == 422
