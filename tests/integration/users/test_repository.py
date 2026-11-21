"""Integration checks for user persistence wiring."""


def test_users_repository_module_imports() -> None:
    from app.modules.users import repository

    assert repository is not None
