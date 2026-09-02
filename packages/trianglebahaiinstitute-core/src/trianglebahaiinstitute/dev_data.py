"""Development seed helpers."""

from sqlmodel import Session


def seed(session: Session) -> None:
    """Populate development seed data.

    Currently a no-op placeholder.
    """
    _ = session
