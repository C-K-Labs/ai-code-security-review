import sqlite3

DB_NAME = "users.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                age INTEGER NOT NULL
            )
        """)
        conn.commit()


def add_user(name, email, age):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, age)
                VALUES (?, ?, ?)
            """, (name, email, age))
            conn.commit()
            print(f"User added successfully with ID: {cursor.lastrowid}")
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        print("Error: Email address already exists.")


def get_user_by_id(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users
            WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

        if user:
            print("User found:")
            print(user)
        else:
            print("User not found.")

        return user


def get_all_users():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        print("All users:")
        for user in users:
            print(user)

        return users


def update_user(user_id, name=None, email=None, age=None):
    with connect_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users
            WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

        if not user:
            print("User not found.")
            return

        new_name = name if name is not None else user[1]
        new_email = email if email is not None else user[2]
        new_age = age if age is not None else user[3]

        try:
            cursor.execute("""
                UPDATE users
                SET name = ?, email = ?, age = ?
                WHERE id = ?
            """, (new_name, new_email, new_age, user_id))
            conn.commit()
            print("User updated successfully.")
        except sqlite3.IntegrityError:
            print("Error: Email address already exists.")


def delete_user(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM users
            WHERE id = ?
        """, (user_id,))
        conn.commit()

        if cursor.rowcount > 0:
            print("User deleted successfully.")
        else:
            print("User not found.")


def demo():
    print("Creating users table...")
    create_table()

    print("\nAdding users...")
    user1_id = add_user("Abner Flores", "abner@example.com", 21)
    user2_id = add_user("John Smith", "john@example.com", 25)

    print("\nRetrieving user by ID...")
    get_user_by_id(user1_id)

    print("\nRetrieving all users...")
    get_all_users()

    print("\nUpdating user...")
    update_user(user1_id, name="Abner F.", age=22)

    print("\nRetrieving updated user...")
    get_user_by_id(user1_id)

    print("\nDeleting user...")
    delete_user(user2_id)

    print("\nRetrieving all users after deletion...")
    get_all_users()


if __name__ == "__main__":
    demo()