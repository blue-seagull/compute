import sqlite3
import sys

def connect_db():
    return sqlite3.connect("/path/to/user_directory.db")

def verify_compute_id(compute_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE compute_id = ?", (compute_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def main():
    compute_id = input("Enter your Compute ID: ").strip()
    user = verify_compute_id(compute_id)

    if user:
        print(f"Welcome {user[0]}! Remote access granted.")
        sys.exit(0)  # Exit successfully
    else:
        print("Invalid Compute ID. Access denied.")
        sys.exit(1)  # Exit with failure status

if __name__ == "__main__":
    main()