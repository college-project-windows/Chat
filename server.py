from flask import Flask, request
from flask_socketio import SocketIO, send
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")  # Add your Firebase credentials JSON
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    return "Chat Server is Running"

@socketio.on('message')
def handle_message(msg):
    print(f"Message received: {msg}")
    send(msg, broadcast=True)

    # Save message to Firebase
    db.collection("messages").add({"message": msg})

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
