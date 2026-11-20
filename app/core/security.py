"""Application security primitives."""

from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Create a password hash using the application's configured algorithm."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored hash."""
    return password_hasher.verify(plain_password, hashed_password)


__all__ = ["hash_password", "verify_password"]
