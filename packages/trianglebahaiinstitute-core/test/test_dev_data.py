from unittest.mock import MagicMock

from trianglebahaiinstitute.dev_data import seed
from trianglebahaiinstitute.errors import AuthorizationError


def test_seed_accepts_session_and_is_noop() -> None:
    # Arrange
    session = MagicMock()

    # Act
    result = seed(session)

    # Assert
    assert result is None


def test_authorization_error_is_exception_type() -> None:
    # Arrange / Act
    error = AuthorizationError("forbidden")

    # Assert
    assert isinstance(error, Exception)
    assert str(error) == "forbidden"
