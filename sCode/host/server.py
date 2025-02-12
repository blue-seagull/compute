from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to Bodega Compute!"})

@app.route("/bodega/create", methods=["POST"])
def create_bodega():
    data = request.json
    enterprise_name = data.get("enterprise_name")

    # Example: Create a Bodega using Docker
    container_name = f"bodega-{enterprise_name.lower().replace(' ', '-')}"
    subprocess.run(["docker", "run", "-d", "--name", container_name, "ubuntu"])

    return jsonify({"message": f"Bodega for {enterprise_name} created successfully!", "container": container_name})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)