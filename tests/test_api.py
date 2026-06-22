from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import checks as checks_routes


def test_health_and_readiness_endpoints_are_available(client):
    health_response = client.get("/api/v1/health")
    ready_response = client.get("/api/v1/ready")

    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"
    assert ready_response.status_code == 200
    assert ready_response.json() == {"status": "ready"}


def test_create_and_fetch_check(client):
    response = client.post(
        "/api/v1/checks",
        json={
            "company_name": "Global Cargo Risk",
            "tax_id": "7701234567",
            "country": "ru",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["severity"] == "high"
    assert payload["country"] == "RU"
    assert payload["signals"]
    assert "status" not in payload

    check_id = payload["id"]
    fetch_response = client.get(f"/api/v1/checks/{check_id}")
    assert fetch_response.status_code == 200
    assert fetch_response.json()["id"] == check_id


def test_list_checks_returns_pagination_metadata(client):
    for index in range(2):
        create_response = client.post(
            "/api/v1/checks",
            json={"company_name": f"Counterparty {index}", "tax_id": f"12345{index}"},
        )
        assert create_response.status_code == 201

    response = client.get("/api/v1/checks?limit=1&offset=0")
    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 2
    assert payload["limit"] == 1
    assert len(payload["items"]) == 1


def test_create_check_rejects_invalid_tax_id(client):
    response = client.post(
        "/api/v1/checks",
        json={"company_name": "Example Company", "tax_id": "ABC-123!"},
    )

    assert response.status_code == 422
    assert "Tax ID" in response.text


def test_create_check_rejects_invalid_country_code(client):
    response = client.post(
        "/api/v1/checks",
        json={"company_name": "Example Company", "country": "DEU"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "country"


def test_create_check_returns_500_when_persistence_fails(client, monkeypatch):
    def raise_persistence_error(*args, **kwargs):
        raise SQLAlchemyError("db unavailable")

    monkeypatch.setattr(checks_routes, "create_check_result", raise_persistence_error)

    response = client.post(
        "/api/v1/checks",
        json={"company_name": "Northwind Consulting", "tax_id": "DE-5523419", "country": "DE"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to persist the risk check result."
