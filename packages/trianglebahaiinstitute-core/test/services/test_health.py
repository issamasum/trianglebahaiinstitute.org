from unittest.mock import patch

from trianglebahaiinstitute.services.health import get_health_status


def test_get_health_status_returns_app_and_environment() -> None:
    # Arrange / Act
    with patch("trianglebahaiinstitute.services.health.Settings") as settings_cls:
        settings_cls.return_value.app_name = "trianglebahaiinstitute"
        settings_cls.return_value.environment = "test"
        result = get_health_status()

    # Assert
    assert result == {
        "status": "ok",
        "app": "trianglebahaiinstitute",
        "environment": "test",
    }
