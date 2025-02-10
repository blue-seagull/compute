from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import uuid

userDB_server = Flask(__name__)
CORS(userDB_server)

# Connects to the "user_directory.db" SQLite Database, and creates it if it doesnt already exist
def connect_db():
    conn = sqlite3.connect("user_directory.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        database_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        compute_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT UNIQUE
                    )''')
    conn.commit()
    return conn

# Generates Blue Seagull Compute ID
def generate_compute_id():
    return str(uuid.uuid4())

# Converts users info from python to JSON and saves it in the database
@userDB_server.route('/', methods=['POST'])
def save_user():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        compute_id = generate_compute_id()
        
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO users (compute_id, name, email, phone) VALUES (?, ?, ?, ?)",
                       (compute_id, name, email, phone))
        conn.commit()
        conn.close()

        return jsonify({"message": "User added successfully!", "compute_id": compute_id}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email or phone already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@userDB_server.route('/auth', methods=['POST'])
def authenticate_user():
    try:
        data = request.json
        name = data.get('name')
        compute_id = data.get('compute_id')

        if not name or not compute_id:
            return jsonify({"error": "Missing name or compute ID"}), 400

        conn = connect_db()
        cursor = conn.cursor()

        # Check if user exists and the name matches the compute ID
        cursor.execute("SELECT name FROM users WHERE compute_id = ?", (compute_id,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == name:
            return jsonify({"message": "Authentication successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@userDB_server.route('/user', methods=['GET'])
def get_user_data():
    try:
        compute_id = request.args.get('compute_id')

        if not compute_id:
            return jsonify({"error": "Compute ID is required"}), 400

        conn = connect_db()
        cursor = conn.cursor()

        # Fetch user data based on Compute ID
        cursor.execute("SELECT name, email FROM users WHERE compute_id = ?", (compute_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            name, email = result
            return jsonify({
                "name": name,
                "email": email,
                "billing_total": 120.50,  # Example billing data
                "billing_date": "March 15, 2025"
            }), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    userDB_server.run(debug=True)