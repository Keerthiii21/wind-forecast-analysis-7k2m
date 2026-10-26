
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "gridbricks-wind-api",
    }


def test_actuals_rejects_invalid_date_range():
    response = client.get(
        "/api/actuals",
        params={
            "start_date": "2026-01-31",
            "end_date": "2026-01-01",
        },
    )

    assert response.status_code == 400


def test_forecasts_rejects_invalid_date_range():
    response = client.get(
        "/api/forecasts",
        params={
            "start_date": "2026-01-31",
            "end_date": "2026-01-01",
        },
    )

    assert response.status_code == 400


def test_analysis_rejects_invalid_date_range():
    response = client.get(
        "/api/analysis",
        params={
            "start_date": "2026-01-31",
            "end_date": "2026-01-01",
        },
    )

    assert response.status_code == 400


def test_analysis_rejects_ranges_longer_than_32_days():
    response = client.get(
        "/api/analysis",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-02-02",
        },
    )

    assert response.status_code == 400
