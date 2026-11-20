"""Integration checks for messaging infrastructure."""


def test_messaging_package_imports() -> None:
    from app.infrastructure import messaging

    assert messaging is not None
