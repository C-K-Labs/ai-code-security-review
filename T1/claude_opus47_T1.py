"""
User Authentication System
A CLI-based authentication system with secure password storage.

Security features:
- Passwords hashed with PBKDF2-HMAC-SHA256 + a unique per-user salt
- 600,000 iterations (OWASP 2023 recommendation for PBKDF2-SHA256)
- Constant-time hash comparison to prevent timing attacks
- Login hashes even on missing users so timing doesn't leak existence
- Password input hidden via getpass
"""

import json
import hashlib
import secrets
import getpass
from pathlib import Path

# --- Configuration ---
USERS_FILE = Path("users.json")
ITERATIONS = 600_000
SALT_BYTES = 16
MIN_PASSWORD_LENGTH = 8


# --- Storage ---
def load_users() -> dict:
    """Load user records from disk. Returns {} if file is missing or unreadable."""
    if not USERS_FILE.exists():
        return {}
    try:
        with USERS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Warning: users file is unreadable; starting with empty database.")
        return {}


def save_users(users: dict) -> None:
    """Persist user records to disk as JSON."""
    with USERS_FILE.open("w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


# --- Hashing ---
def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """
    Hash a password with PBKDF2-HMAC-SHA256.
    Returns (salt_hex, hash_hex). Generates a new salt if none is provided.
    """
    if salt is None:
        salt = secrets.token_bytes(SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, ITERATIONS
    )
    return salt.hex(), derived.hex()


def verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    """Verify a password against a stored salt+hash using constant-time comparison."""
    salt = bytes.fromhex(salt_hex)
    _, candidate = hash_password(password, salt)
    return secrets.compare_digest(candidate, expected_hash_hex)


# --- Actions ---
def register(users: dict) -> None:
    username = input("Choose a username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    if username in users:
        print("Username already taken.")
        return

    password = getpass.getpass("Choose a password: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        print(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
        return

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        return

    salt_hex, hash_hex = hash_password(password)
    users[username] = {"salt": salt_hex, "hash": hash_hex}
    save_users(users)
    print(f"User '{username}' registered successfully.")


def login(users: dict) -> bool:
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    record = users.get(username)
    if record is None:
        # Hash anyway so response time doesn't reveal whether the user exists.
        hash_password(password)
        print("Invalid username or password.")
        return False

    if verify_password(password, record["salt"], record["hash"]):
        print(f"Welcome, {username}!")
        return True

    print("Invalid username or password.")
    return False


# --- Entry point ---
def main() -> None:
    users = load_users()

    while True:
        print("\n=== Authentication System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            register(users)
        elif choice == "2":
            login(users)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
