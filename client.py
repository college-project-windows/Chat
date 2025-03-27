import sys
import asyncio
import websockets
import rsa
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

# Generate RSA keys for encryption (public & private)
public_key, private_key = rsa.newkeys(512)

# Server WebSocket URL (Change this to your Render URL)
SERVER_URL = "https://chat-rde3.onrender.com"

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()

        # Set up UI
        self.setWindowTitle("Secure Chat Client")
        self.setGeometry(100, 100, 400, 500)

        self.layout = QVBoxLayout()

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.message_input = QLineEdit(self)
        self.layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

        # Start WebSocket connection
        self.websocket = None
        asyncio.ensure_future(self.connect_to_server())

    async def connect_to_server(self):
        """Connects to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(SERVER_URL)

            # Send public key to the server
            await self.websocket.send(public_key.save_pkcs1().decode())

            while True:
                encrypted_message = await self.websocket.recv()
                decrypted_message = rsa.decrypt(encrypted_message.encode(), private_key).decode()
                self.chat_display.append(f"Server: {decrypted_message}")
        except Exception as e:
            self.chat_display.append(f"Error: {e}")

    def send_message(self):
        """Sends encrypted message to the WebSocket server"""
        message = self.message_input.text()
        if message and self.websocket:
            asyncio.ensure_future(self.send_encrypted_message(message))
            self.message_input.clear()

    async def send_encrypted_message(self, message):
        """Encrypts and sends a message"""
        encrypted_message = rsa.encrypt(message.encode(), public_key).decode()
        await self.websocket.send(encrypted_message)
        self.chat_display.append(f"You: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())
