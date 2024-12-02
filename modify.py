import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QCheckBox, QInputDialog, QScrollArea, QGridLayout, QMessageBox
)

QUIZZES_FILE = "quizzes.json"
QUESTIONS_FILE = "questions.json"


class ModifyQuizInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modify Quiz")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Load quizzes
        self.quizzes = self.load_json(QUIZZES_FILE)
        if not self.quizzes:
            QMessageBox.warning(self, "Error", "No quizzes available!")
            return

        # Display quiz buttons
        layout.addWidget(QLabel("Select a Quiz to Modify:"))
        self.quiz_buttons = []
        for quiz in self.quizzes:
            button = QPushButton(quiz.get("quiz_title", "Untitled Quiz"))
            button.clicked.connect(self.ask_quiz_password)
            self.quiz_buttons.append((button, quiz))
            layout.addWidget(button)

        self.setLayout(layout)

    def ask_quiz_password(self):
        """Ask the password for the selected quiz."""
        button = self.sender()
        quiz = next(q for b, q in self.quiz_buttons if b == button)

        self.password_window = QWidget()
        self.password_window.setWindowTitle("Enter Password")
        self.password_window.setGeometry(150, 150, 300, 150)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Enter password for quiz: {quiz.get('quiz_title', 'Untitled Quiz')}"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(lambda: self.verify_password(quiz))
        layout.addWidget(submit_button)

        self.password_window.setLayout(layout)
        self.password_window.show()

    def verify_password(self, quiz):
        """Verify the entered password and proceed if correct."""
        entered_password = self.password_input.text()
        if entered_password == quiz.get("quiz_password", ""):
            self.password_window.close()
            self.show_question_list(quiz)
        else:
            QMessageBox.warning(self.password_window, "Error", "Incorrect password!")

    def show_question_list(self, quiz):
        """Display a list of questions for the selected quiz."""
        self.question_window = QWidget()
        self.question_window.setWindowTitle(f"Questions for {quiz.get('quiz_title', 'Untitled Quiz')}")
        self.question_window.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Questions in Quiz: {quiz.get('quiz_title', 'Untitled Quiz')}"))

        # Load questions for the quiz
        questions = self.load_json(QUESTIONS_FILE)
        self.quiz_questions = [q for q in questions if q.get("quiz_title") == quiz.get("quiz_title")]

        self.question_buttons = []
        for idx, question in enumerate(self.quiz_questions, start=1):
            button = QPushButton(f"Q{idx}: {question.get('question', 'No Question Text')}")
            button.clicked.connect(self.modify_question)
            self.question_buttons.append((button, question))
            layout.addWidget(button)

        change_time_button = QPushButton(f"Change Quiz Time (Current: {quiz.get('total_time', 'N/A')} minutes)")
        change_time_button.clicked.connect(lambda: self.change_quiz_time(quiz))
        layout.addWidget(change_time_button)

        change_password_button = QPushButton(f"Change Quiz Password (Current: {quiz.get('quiz_password', 'N/A')})")
        change_password_button.clicked.connect(lambda: self.change_quiz_password(quiz))
        layout.addWidget(change_password_button)

        self.question_window.setLayout(layout)
        self.question_window.show()

    def modify_question(self):
        """Open the modification interface for the selected question."""
        button = self.sender()
        question = next(q for b, q in self.question_buttons if b == button)

        self.modify_window = QWidget()
        self.modify_window.setWindowTitle("Modify Question")
        self.modify_window.setGeometry(150, 150, 500, 400)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Modify Question: {question.get('question', 'No Question Text')}"))

        # Disable changing the question type
        layout.addWidget(QLabel(f"Question Type: {question.get('question_type', 'Unknown')}"))

        self.question_inputs = {}
        for key, value in question.items():
            if key in ["quiz_title", "question_type"]:
                continue  # Don't modify quiz_title and question_type
            layout.addWidget(QLabel(f"{key.capitalize()}:"))
            input_field = QLineEdit(str(value))
            layout.addWidget(input_field)
            self.question_inputs[key] = input_field

        if question.get("question_type") == "Multiple Correct Answer":
            self.show_mca_options(question, layout)

        save_button = QPushButton("Save Modification")
        save_button.clicked.connect(lambda: self.save_modification(question))
        layout.addWidget(save_button)

        modify_other_button = QPushButton("Modify Another Question")
        modify_other_button.clicked.connect(self.back_to_question_list)
        layout.addWidget(modify_other_button)

        self.modify_window.setLayout(layout)
        self.modify_window.show()

    def show_mca_options(self, question, layout):
        """Show options with checkboxes for MCA questions and allow adding more options."""
        layout.addWidget(QLabel("Options:"))
        
        # Show current options
        self.option_checkboxes = []
        for idx, option in enumerate(question["answers"]["options"]):
            checkbox = QCheckBox(option)
            # Check if it's marked as a correct answer
            checkbox.setChecked(idx + 1 in question["answers"]["correct_answers"])
            layout.addWidget(checkbox)
            self.option_checkboxes.append(checkbox)

        # Add "Add More Options" button
        self.add_option_button = QPushButton("Add More Options")
        self.add_option_button.clicked.connect(self.add_mca_option)
        layout.addWidget(self.add_option_button)

    def add_mca_option(self):
        """Add a new option to the MCA question."""
        new_option, ok = QInputDialog.getText(self, "Add Option", "Enter the new option:")
        if ok and new_option:
            checkbox = QCheckBox(new_option)
            self.option_checkboxes.append(checkbox)
            self.modify_window.layout().insertWidget(len(self.option_checkboxes) - 1, checkbox)
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a valid option.")

    def save_modification(self, question):
        """Save the modified question back to the file."""
        for key, input_field in self.question_inputs.items():
            value = input_field.text()
            if key == "marks":
                try:
                    value = int(value)
                except ValueError:
                    QMessageBox.warning(self, "Error", "Marks must be a number!")
                    return
            question[key] = value

        # Ensure `answers` is a dictionary
        if not isinstance(question.get("answers"), dict):
            question["answers"] = {
                "options": [],
                "correct_answers": []
            }

        # Save the new options added by the user
        question["answers"]["options"] = [checkbox.text() for checkbox in self.option_checkboxes]
        question["answers"]["correct_answers"] = [
            idx + 1 for idx, checkbox in enumerate(self.option_checkboxes) if checkbox.isChecked()
        ]

        # Save to file
        self.save_questions()
        QMessageBox.information(self.modify_window, "Success", "Question modified successfully!")


    # Save to file
        self.save_questions()
        QMessageBox.information(self.modify_window, "Success", "Question modified successfully!")

    def back_to_question_list(self):
        """Return to the question list."""
        self.modify_window.close()

    def change_quiz_time(self, quiz):
        """Change the time for the selected quiz."""
        time, ok = QInputDialog.getText(self, "Change Time", f"Enter new time (current: {quiz['total_time']}):")
        if ok:
            try:
                quiz["total_time"] = int(time)
                self.save_quizzes()
                QMessageBox.information(self, "Success", "Quiz time updated!")
            except ValueError:
                QMessageBox.warning(self, "Error", "Please enter a valid number for time!")

    def change_quiz_password(self, quiz):
        """Change the password for the selected quiz."""
        password, ok = QInputDialog.getText(self, "Change Password", f"Enter new password (current: {quiz['quiz_password']}):")
        if ok:
            quiz["quiz_password"] = password
            self.save_quizzes()
            QMessageBox.information(self, "Success", "Quiz password updated!")

    def load_json(self, file_name):
        """Load JSON data from a file."""
        try:
            with open(file_name, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_questions(self):
        """Save questions back to the file."""
        with open(QUESTIONS_FILE, "w") as f:
            json.dump(self.quiz_questions, f, indent=4)

    def save_quizzes(self):
        """Save quizzes back to the file."""
        with open(QUIZZES_FILE, "w") as f:
            json.dump(self.quizzes, f, indent=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    interface = ModifyQuizInterface()
    interface.show()
    sys.exit(app.exec_())