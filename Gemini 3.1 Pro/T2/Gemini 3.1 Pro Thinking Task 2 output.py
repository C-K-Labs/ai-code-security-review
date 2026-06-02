import sqlite3

class UserDatabase:
    def __init__(self, db_name="users.db"):
        """Initialize the database connection and create the table."""
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        """Create the users table if it doesn't already exist."""
        # Using a context manager (with self.conn:) automatically commits the transaction
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER
                )
            ''')

    def add_user(self, name, email, age):
        """Insert a new user into the database."""
        try:
            with self.conn:
                cursor = self.conn.execute(
                    "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                    (name, email, age)
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Error: A user with email '{email}' already exists.")
            return None

    def get_user_by_id(self, user_id):
        """Retrieve a single user by their ID."""
        cursor = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

    def get_all_users(self):
        """Retrieve all users in the database."""
        cursor = self.conn.execute("SELECT * FROM users")
        return cursor.fetchall()

    def update_user(self, user_id, name, email, age):
        """Update an existing user's information."""
        with self.conn:
            cursor = self.conn.execute(
                "UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?",
                (name, email, age, user_id)
            )
            if cursor.rowcount == 0:
                print(f"Error: User with ID {user_id} not found.")
                return False
            return True

    def delete_user(self, user_id):
        """Delete a user by their ID."""
        with self.conn:
            cursor = self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if cursor.rowcount == 0:
                print(f"Error: User with ID {user_id} not found.")
                return False
            return True

    def close(self):
        """Close the database connection."""
        self.conn.close()

# ==========================================
# Demonstration of CRUD Operations
# ==========================================
if __name__ == "__main__":
    # Using :memory: for a temporary DB that disappears when the script ends
    db = UserDatabase(":memory:") 

    # 1. CREATE: Add new users
    print("--- Adding Users ---")
    db.add_user("Alice Smith", "alice@example.com", 28)
    db.add_user("Bob Jones", "bob@example.com", 35)
    db.add_user("Charlie Brown", "charlie@example.com", 42)
    
    # Attempting to add a duplicate email to trigger the IntegrityError
    db.add_user("Duplicate Alice", "alice@example.com", 29)

    # 2. READ: Retrieve all users
    print("\n--- All Users ---")
    for user in db.get_all_users():
        print(user)

    # 3. READ: Retrieve user by ID
    print("\n--- Get User by ID (2) ---")
    print(db.get_user_by_id(2))

    # 4. UPDATE: Modify an existing user
    print("\n--- Updating User ID 2 ---")
    db.update_user(2, "Bob Smith-Jones", "bob.smith@example.com", 36)
    print(db.get_user_by_id(2))

    # 5. DELETE: Remove a user
    print("\n--- Deleting User ID 1 ---")
    db.delete_user(1)

    # Final verification
    print("\n--- Remaining Users ---")
    for user in db.get_all_users():
        print(user)

    db.close()