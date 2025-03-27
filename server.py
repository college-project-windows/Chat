import os
import json
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load Firebase credentials from environment variable
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_credentials_json:
    raise ValueError("Firebase credentials not found!")

# Parse the JSON string
firebase_credentials = json.loads(firebase_credentials_json)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)

# Firestore database
db = firestore.client()

# Store connected users
users = {}

@app.route("/")
def home():
    return "Chat server is running!"

# WebSocket connection
@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in users:
        print(f"Client {users[request.sid]} disconnected")
        del users[request.sid]
    else:
        print(f"Client {request.sid} disconnected")

# Join chat room
@socketio.on("join")
def handle_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    users[request.sid] = username
    send(f"{username} has joined the chat!", to=room)

# Leave chat room
@socketio.on("leave")
def handle_leave(data):
    username = users.get(request.sid, "Unknown User")
    room = data["room"]
    leave_room(room)
    send(f"{username} has left the chat!", to=room)

# Handle chat messages
@socketio.on("message")
def handle_message(data):
    username = users.get(request.sid, "Unknown User")
    message = data["message"]
    room = data["room"]

    # Store message in Firestore
    db.collection("chats").add({
        "username": username,
        "message": message,
        "room": room
    })

    send(f"{username}: {message}", to=room)

# Run Flask app with WebSockets
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
