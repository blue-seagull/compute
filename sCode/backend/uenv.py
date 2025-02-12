import sqlite3

def connect_db():
    return sqlite3.connect("user_directory.db")

def verify_bodega_id(bodega_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT compute_id FROM users WHERE compute_id = ?", (bodega_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def main():
    bodega_id = input("Enter your Bodega ID: ")
    if verify_bodega_id(bodega_id):
        print("Bodega ID is valid.")
        print("Initiate Bodega")
        print("or")
        print("Access Storage")
    else:
        print("Invalid Bodega ID.")

if __name__ == "__main__":
    main()
