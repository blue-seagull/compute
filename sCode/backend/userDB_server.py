from flask import Flask, request, jsonify
import jwt
import datetime
import sqlite3
from flask_cors import CORS
import uuid

userDB_server = Flask(__name__)
CORS(userDB_server)

SECRET_KEY = "your_secret_key"

# Connects to the "user_directory.db" SQLite Database, and creates it if it doesnt already exist
def connect_db():
    conn = sqlite3.connect("/Users/fernandocarrillo/blue42/database/user_directory.db")
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bodega_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT UNIQUE
                    )''')
    conn.commit()
    return conn

# Generates Blue Seagull Bodega ID
def generate_bodega_id():
    return str(uuid.uuid4())

# Save User Route (SIGN UP)
@userDB_server.route('/', methods=['POST'])
def save_user():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        bodega_id = generate_bodega_id()
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (bodega_id, name, email, phone) VALUES (?, ?, ?, ?)",
                       (bodega_id, name, email, phone))
        conn.commit()
        conn.close()

        return jsonify({"message": "User added successfully!", "bodega_id": bodega_id}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email or phone already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Authenticate the User Route (JWT) (SIGN IN)
@userDB_server.route('/auth', methods=['POST'])
def authenticate_user():
    try:
        data = request.json
        name = data.get('name')
        bodega_id = data.get('bodega_id')

        print(f"Received Login Request: name={name}, bodega_id={bodega_id}")

        if not name or not bodega_id:
            print("Missing name or Bodega ID")
            return jsonify({"error": "Missing name or Bodega ID"}), 400

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name, bodega_id FROM users WHERE bodega_id = ?", (bodega_id,))
        result = cursor.fetchone()
        conn.close()

        print(f"Query Result: {result}")

        if result and result[0].strip().lower() == name.strip().lower() and result[1] == bodega_id:
            token = jwt.encode(
                {"bodega_id": bodega_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                SECRET_KEY,
                algorithm="HS256"
            )
            print(f"Generated Token: {token}")
            return jsonify({"token": token}), 200
        else:
            print("Invalid credentials")
            return jsonify({"error": "Invalid credentials"}), 401
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Get User Data Route (Protected) (ACCESS DASHBOARD)
@userDB_server.route('/user', methods=['GET'])
def get_user_data():
    """Retrieve user data using JWT token authentication"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized, no token provided"}), 401

    token = auth_header.split(" ")[1]  # Extract JWT token

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        bodega_id = decoded_token["bodega_id"]

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name, bodega_id FROM users WHERE bodega_id = ?", (bodega_id,))
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

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired, please log in again"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

if __name__ == "__main__":
    userDB_server.run(debug=True)