import os
import json
import base64
import rsa
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request
from flask_socketio import SocketIO, send, emit

# Initialize Flask App
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 🔐 Load Firebase Credentials (Use environment variable for security)
firebase_cred = os.getenv("FIREBASE_CREDENTIALS")
if firebase_cred:
    cred_dict = json.loads(base64.b64decode(firebase_cred).decode("utf-8"))
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    raise ValueError("Firebase credentials not found!")

# 🔑 RSA Key Generation for End-to-End Encryption
(pub_key, priv_key) = rsa.newkeys(512)

# Store connected clients
clients = {}

@app.route('/')
def home():
    return "Chat server is running!"

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    clients[request.sid] = pub_key  # Store public key for encryption
    emit("public_key", pub_key.save_pkcs1().decode(), room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    clients.pop(request.sid, None)

@socketio.on('message')
def handle_message(data):
    try:
        encrypted_message = data.get("message")
        sender = data.get("sender")

        # Decrypt message
        decrypted_message = rsa.decrypt(base64.b64decode(encrypted_message), priv_key).decode()

        print(f"Received message from {sender}: {decrypted_message}")

        # Store message in Firebase Firestore
        db.collection("chats").add({
            "sender": sender,
            "message": decrypted_message
        })

        # Broadcast decrypted message to all clients
        emit("message", {"sender": sender, "message": decrypted_message}, broadcast=True)

    except Exception as e:
        print(f"Error handling message: {e}")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=10000)
