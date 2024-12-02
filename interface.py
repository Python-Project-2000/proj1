import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QComboBox
)
# from PyQt5.QtCore import Qt
from main_admin import AdminInterface
from main_user import UserInterface
from modify import ModifyQuizInterface

# File to store user credentials
CREDENTIALS_FILE = "credentials.json"


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Management System - Login")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Role selection
        self.role_label = QLabel("Select Role:")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Admin", "User"])

        # Username and Password
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        # Buttons
        self.login_button = QPushButton("Login")
        self.register_button = QPushButton("Register")

        # Add to layout
        layout.addWidget(self.role_label)
        layout.addWidget(self.role_combo)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        # Connect buttons to functions
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def load_credentials(self):
        """Load credentials from the file."""
        try:
            with open(CREDENTIALS_FILE, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_credentials(self, credentials):
        """Save credentials to the file."""
        with open(CREDENTIALS_FILE, "w") as file:
            json.dump(credentials, file)

    def login(self):
        """Handle login functionality."""
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()

        credentials = self.load_credentials()

        if username in credentials and credentials[username]["password"] == password:
            if credentials[username]["role"] == role:
                # QMessageBox.information(self, "Success", f"Welcome {role}!")
                # Proceed to respective interface (Admin or User)
                self.open_dashboard(role, username)
            else:
                QMessageBox.warning(self, "Error", "Role mismatch!")
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials!")

    def register(self):
        """Handle user registration."""
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill all fields!")
            return

        credentials = self.load_credentials()

        if username in credentials:
            QMessageBox.warning(self, "Error", "Username already exists!")
        else:
            credentials[username] = {"password": password, "role": role}
            self.save_credentials(credentials)
            QMessageBox.information(self, "Success", "Registration successful!")
            self.open_dashboard(role, username)

    def open_dashboard(self, role, username):
        """Open Admin or User dashboard."""
        if role == "Admin":
            QMessageBox.information(self, "Info","Welcome Admin")
            self.start_admin_interface()
        elif role == "User":
            QMessageBox.information(self, "Info", "Welcome User")
            # User interface logic here
            self.start_user_interface(username)
            
    def start_admin_interface(self):
        """Start the admin interface."""
        self.admin_window = AdminOptionsInterface()
        self.admin_window.show()

    def start_user_interface(self, username):
        """Start the user interface."""
        self.user_window = UserInterface(username)
        self.user_window.show()

class AdminOptionsInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Option Buttons
        self.create_quiz_button = QPushButton("Create Quiz")
        self.modify_quiz_button = QPushButton("Modify Quiz")

        # Add buttons to layout
        layout.addWidget(QLabel("Admin Options:"))
        layout.addWidget(self.create_quiz_button)
        layout.addWidget(self.modify_quiz_button)

        self.setLayout(layout)

        # Connect buttons to respective functions
        self.create_quiz_button.clicked.connect(self.open_create_quiz)
        self.modify_quiz_button.clicked.connect(self.open_modify_quiz)

    def open_create_quiz(self):
        """Open the Create Quiz interface."""
        self.create_quiz_window = AdminInterface()
        self.create_quiz_window.show()

    def open_modify_quiz(self):
        """Open the Modify Quiz interface."""
        self.modify_quiz_window = ModifyQuizInterface()
        self.modify_quiz_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
