import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal
import socketio

# Connect to server
sio = socketio.Client()

class ChatClient(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chat App")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        layout.addWidget(self.chat_area)
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)
        self.setLayout(layout)

        # Connect to WebSocket server
        sio.connect("http://localhost:5000")  # Change to Render URL after deployment
        sio.on("message", self.receive_message)

    def send_message(self):
        message = self.input_field.text()
        if message:
            sio.emit("message", message)
            self.input_field.clear()

    def receive_message(self, msg):
        self.chat_area.append(f"Friend: {msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec())
