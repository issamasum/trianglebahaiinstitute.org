from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


from api.routes.health import health


def test_health_route_function_returns_health_status() -> None:
    # Arrange
    expected_status = {
        "status": "ok",
        "app": "trianglebahaiinstitute",
        "environment": "test",
    }

    # Act
    with patch("api.routes.health.get_health_status", return_value=expected_status):
        response = health()

    # Assert
    assert response == expected_status


@pytest.mark.integration
def test_health_endpoint_returns_json_payload(client: TestClient) -> None:
    # Arrange
    expected_status = {"status": "ok", "app": "api-test", "environment": "test"}

    # Act
    with patch("api.routes.health.get_health_status", return_value=expected_status):
        response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_status
