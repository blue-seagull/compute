from flask import Flask, request, jsonify
import jwt
import datetime
import psycopg2
from flask_cors import CORS
import uuid
import docker
import os
import logging

userDB_server = Flask(__name__)
CORS(userDB_server)

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 1))
BASE_SSH_PORT = 2200
DATA_PATH = "/bodega-data"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "blue42")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def connect_db():
    """Establish a PostgreSQL database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    """Execute SQL queries using PostgreSQL with proper connection handling."""
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        if commit:
            conn.commit()

        if fetchone:
            return cursor.fetchone()
        elif fetchall:
            return cursor.fetchall()
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

def generate_bodega_id():
    return str(uuid.uuid4())[:8]

def create_bodega_container(bodega_id):
    client = docker.from_env()

    active_bodegas = len(client.containers.list(all=True, filters={"name": "bodega-"}))
    ssh_port = BASE_SSH_PORT + active_bodegas

    storage_path = os.path.join(DATA_PATH, bodega_id)
    os.makedirs(storage_path, exist_ok=True)

    container = client.containers.run(
        "bodega-image",
        name=f"bodega-{bodega_id}",
        detach=True,
        ports={"22/tcp": ssh_port},
        volumes={storage_path: {'bind': '/bodega-storage', 'mode': 'rw'}}
    )
    logging.info(f"Bodega {bodega_id} created with SSH port {ssh_port}")
    return {"container_id": container.id, "ssh_port": ssh_port}

@userDB_server.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        name, email, phone = data.get('name'), data.get('email'), data.get('phone')
        if not all([name, email, phone]):
            return jsonify({"error": "Missing required fields"}), 400
        bodega_id = generate_bodega_id()
        execute_query(
            "INSERT INTO users (bodega_id, name, email, phone) VALUES (%s, %s, %s, %s)",
            (bodega_id, name, email, phone),
            commit=True
        )
        return jsonify({
            "message": "User registered successfully!",
            "bodega_id": bodega_id
        }), 201
    except psycopg2.IntegrityError:
        return jsonify({"error": "Email or phone already exists"}), 400
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@userDB_server.route('/auth', methods=['POST'])
def authenticate_user():
    try:
        data = request.json
        name, bodega_id = data.get('name'), data.get('bodega_id')
        if not name or not bodega_id:
            return jsonify({"error": "Missing name or Bodega ID"}), 400
        result = execute_query(
            "SELECT name, bodega_id FROM users WHERE bodega_id = %s",
            (bodega_id,),
            fetchone=True
        )
        if result and result[0].strip().lower() == name.strip().lower():
            token = jwt.encode(
                {"bodega_id": bodega_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)},
                SECRET_KEY,
                algorithm="HS256"
            )
            return jsonify({"token": token}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Authentication error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@userDB_server.route('/user', methods=['GET'])
def get_user_data():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized, no token provided"}), 401
    token = auth_header.split(" ")[1]

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        bodega_id = decoded_token["bodega_id"]
        result = execute_query(
            "SELECT name, email, bodega_id FROM users WHERE bodega_id = %s",
            (bodega_id,),
            fetchone=True
        )
        container_info = execute_query(
            "SELECT ssh_port FROM bodegas WHERE bodega_id = %s",
            (bodega_id,),
            fetchone=True
        )
        if result:
            return jsonify({
                "name": result[0],
                "email": result[1],
                "bodega_id": result[2],
                "ssh_port": container_info[0] if container_info else "N/A"
            }), 200
        return jsonify({"error": "User not found"}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired, please log in again"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    userDB_server.run(debug=True, threaded=False)