import json
import os
import hashlib
import secrets

class AuthenticationSystem:
    def __init__(self, database_file='users.json'):
        """Initializes the auth system and loads existing user data."""
        self.db_file = database_file
        self.users = self._load_users()

    def _load_users(self):
        """Loads user data from the JSON file. Returns an empty dict if it doesn't exist."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_users(self):
        """Saves the current user data back to the JSON file."""
        with open(self.db_file, 'w') as file:
            json.dump(self.users, file, indent=4)

    def _hash_password(self, password, salt=None):
        """
        Hashes a password using PBKDF2 and a secure salt.
        If no salt is provided, a new one is generated.
        """
        if salt is None:
            salt = secrets.token_hex(16)
            
        # PBKDF2 is a standard key derivation function that makes brute-forcing difficult
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            salt.encode('utf-8'), 
            100000 # Number of iterations
        )
        return salt, hash_obj.hex()

    def register(self, username, password):
        """Registers a new user."""
        if not username or not password:
            return False, "Username and password cannot be empty."
        
        if username in self.users:
            return False, "Username already exists. Please choose another."

        if len(password) < 6:
            return False, "Password must be at least 6 characters long."

        # Hash the password and store the salt + hash (NEVER the plain password)
        salt, pwd_hash = self._hash_password(password)
        self.users[username] = {
            'salt': salt,
            'hash': pwd_hash
        }
        
        self._save_users()
        return True, f"User '{username}' successfully registered!"

    def login(self, username, password):
        """Authenticates an existing user."""
        if username not in self.users:
            # We return a generic message to avoid revealing which usernames exist
            return False, "Invalid username or password."

        user_data = self.users[username]
        stored_salt = user_data['salt']
        stored_hash = user_data['hash']

        # Hash the provided password with the stored salt
        _, attempt_hash = self._hash_password(password, stored_salt)

        # secrets.compare_digest prevents "timing attacks" by comparing strings in constant time
        if secrets.compare_digest(stored_hash, attempt_hash):
            return True, f"Welcome back, {username}! Login successful."
        else:
            return False, "Invalid username or password."


# ==========================================
# Command Line Interface for Testing
# ==========================================
if __name__ == "__main__":
    auth = AuthenticationSystem()
    print("--- Secure User Authentication System ---")

    while True:
        print("\nOptions:")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Select an option (1/2/3): ")

        if choice == '1':
            user = input("Enter a new username: ").strip()
            pwd = input("Enter a new password: ").strip()
            success, message = auth.register(user, pwd)
            print(f"\n[System]: {message}")

        elif choice == '2':
            user = input("Enter your username: ").strip()
            pwd = input("Enter your password: ").strip()
            success, message = auth.login(user, pwd)
            print(f"\n[System]: {message}")

        elif choice == '3':
            print("Exiting system. Goodbye!")
            break

        else:
            print("\n[System]: Invalid choice. Please select 1, 2, or 3.")