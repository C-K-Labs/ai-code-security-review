import json
import os
import hashlib
import secrets
import hmac

USER_FILE = "users.json"


def load_users():
    if not os.path.exists(USER_FILE):
        return {}

    with open(USER_FILE, "r") as file:
        return json.load(file)


def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    ).hex()

    return salt, password_hash


def register_user():
    users = load_users()

    username = input("Create a username: ").strip()

    if username in users:
        print("That username already exists.")
        return

    password = input("Create a password: ").strip()

    if len(password) < 8:
        print("Password must be at least 8 characters long.")
        return

    salt, password_hash = hash_password(password)

    users[username] = {
        "salt": salt,
        "password_hash": password_hash
    }

    save_users(users)

    print("Registration successful!")


def login_user():
    users = load_users()

    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()

    if username not in users:
        print("Invalid username or password.")
        return

    stored_salt = users[username]["salt"]
    stored_hash = users[username]["password_hash"]

    _, entered_hash = hash_password(password, stored_salt)

    if hmac.compare_digest(stored_hash, entered_hash):
        print(f"Login successful. Welcome, {username}!")
    else:
        print("Invalid username or password.")


def main():
    while True:
        print("\nUser Authentication System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()