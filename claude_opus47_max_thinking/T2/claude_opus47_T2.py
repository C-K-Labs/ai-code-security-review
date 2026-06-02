"""
User Database Manager
A simple SQLite-backed user database supporting CRUD operations.
"""

import sqlite3
from contextlib import contextmanager


class UserDatabase:
    """Manages a SQLite database of users (name, email, age)."""

    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self._create_table()

    @contextmanager
    def _get_connection(self):
        """Context manager that yields a connection and handles commit/rollback."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Allow dict-like access to rows
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _create_table(self):
        """Create the users table if it doesn't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name  TEXT    NOT NULL,
                    email TEXT    NOT NULL UNIQUE,
                    age   INTEGER NOT NULL
                )
            """)

    def add_user(self, name, email, age):
        """Insert a new user and return the generated ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (name, email, age),
            )
            return cursor.lastrowid

    def get_user(self, user_id):
        """Return a user as a dict, or None if not found."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_all_users(self):
        """Return all users as a list of dicts."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
            return [dict(row) for row in rows]

    def update_user(self, user_id, name=None, email=None, age=None):
        """Update one or more fields for a user. Returns True if a row changed."""
        updates, params = [], []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if age is not None:
            updates.append("age = ?")
            params.append(age)

        if not updates:
            return False  # Nothing to update

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return cursor.rowcount > 0

    def delete_user(self, user_id):
        """Delete a user by ID. Returns True if a row was deleted."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

def demonstrate():
    """Run a demonstration of every database operation."""
    import os

    db_file = "demo_users.db"
    if os.path.exists(db_file):
        os.remove(db_file)  # Start fresh each run

    db = UserDatabase(db_file)

    print("=" * 55)
    print(" USER DATABASE DEMONSTRATION")
    print("=" * 55)

    # ---- 1. Adding users ----
    print("\n[1] Adding users...")
    alice_id = db.add_user("Alice Johnson", "alice@example.com", 28)
    bob_id   = db.add_user("Bob Smith",     "bob@example.com",   34)
    carol_id = db.add_user("Carol White",   "carol@example.com", 45)
    print(f"    Added Alice  -> ID {alice_id}")
    print(f"    Added Bob    -> ID {bob_id}")
    print(f"    Added Carol  -> ID {carol_id}")

    # ---- 2. Retrieve a user by ID ----
    print(f"\n[2] Retrieving user with ID {alice_id}...")
    print(f"    {db.get_user(alice_id)}")

    # ---- 3. Retrieve all users ----
    print("\n[3] Retrieving all users...")
    for user in db.get_all_users():
        print(f"    {user}")

    # ---- 4. Update a user ----
    print(f"\n[4] Updating user with ID {bob_id} (name -> 'Robert Smith', age -> 35)...")
    db.update_user(bob_id, name="Robert Smith", age=35)
    print(f"    {db.get_user(bob_id)}")

    # ---- 5. Delete a user ----
    print(f"\n[5] Deleting user with ID {carol_id}...")
    success = db.delete_user(carol_id)
    print(f"    Deletion successful: {success}")

    # ---- 6. Final state ----
    print("\n[6] Final database contents:")
    for user in db.get_all_users():
        print(f"    {user}")

    # Clean up the demo file
    os.remove(db_file)
    print("\n(Demo database file removed.)")


if __name__ == "__main__":
    demonstrate()
