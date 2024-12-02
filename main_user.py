import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox, QInputDialog, QLineEdit, QRadioButton, QCheckBox, QButtonGroup
)
from PyQt5.QtCore import QTimer
from review_updated import QuizSummary


title = None

class UserInterface(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Quiz Management - User Interface")
        self.setGeometry(100, 100, 800, 600)

        # Initialize quiz data and UI elements
        self.quizzes = []  # Store quizzes loaded from quizzes.json
        self.questions = []  # Store questions loaded from questions.json
        self.current_question_index = 0
        self.user_responses = {}  # Stores user responses to questions
        self.timer = None
        self.time_left = 0
        self.timer_label = QLabel("Time Left: 0:00")  # Timer label

        # Layout setup
        self.main_layout = QVBoxLayout()
        self.question_layout = QVBoxLayout()  # Separate layout for questions
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.timer_label)
        self.main_layout.addLayout(self.question_layout)

        self.load_quizzes()
        # s = quiz()
        #s.show_quiz...
        self.show_quiz_selection()

    def load_quizzes(self):
        """Load quizzes from quizzes.json."""
        try:
            with open('quizzes.json', 'r') as file:
                self.quizzes = json.load(file)
        # self.quizzes = quiz()        
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "quizzes.json not found.")
            sys.exit()

    def show_quiz_selection(self):
        """Show the list of available quizzes."""
        self.clear_layout()
        self.question_layout.addWidget(QLabel("Select a Quiz:"))
        for quiz in self.quizzes:
            button = QPushButton(quiz['quiz_title'])
            button.clicked.connect(lambda _, q=quiz: self.prompt_password(q))
            self.question_layout.addWidget(button)

    def prompt_password(self, quiz):
        global title 
        title = quiz
        """Prompt the user for the quiz password."""
        password, ok = QInputDialog.getText(self, "Enter Quiz Password", "Password:")
        if ok and password == quiz['quiz_password']:
            self.show_quiz_details(quiz)
        else:
            QMessageBox.warning(self, "Error", "Incorrect Password!")

    # def show_quiz_details(self, quiz):
    #     """Show quiz details before starting."""
    #     self.clear_layout()
    #     self.question_layout.addWidget(QLabel(f"Quiz Title: {quiz['quiz_title']}"))
    #     self.question_layout.addWidget(QLabel(f"Total Time: {quiz['total_time']} minutes"))
    #     self.question_layout.addWidget(QLabel(f"Total Questions: {quiz['total_questions']}"))
    #     self.question_layout.addWidget(QLabel(f"Total Marks: {quiz['total_marks']}"))

    #     start_button = QPushButton("Start Quiz")
    #     start_button.clicked.connect(lambda: self.start_quiz(quiz))
    #     self.question_layout.addWidget(start_button)
    def show_quiz_details(self, quiz):
        global title
        title = quiz['quiz_title']
        """Show quiz details before starting."""
        self.clear_layout()
        total_minutes = float(quiz['total_time'])
        minutes = int(total_minutes)
        seconds = int((total_minutes - minutes) * 60)
        
        self.question_layout.addWidget(QLabel(f"Quiz Title: {quiz['quiz_title']}"))
        self.question_layout.addWidget(QLabel(f"Total Time: {minutes} minutes {seconds} seconds"))
        self.question_layout.addWidget(QLabel(f"Total Questions: {quiz['total_questions']}"))
        self.question_layout.addWidget(QLabel(f"Total Marks: {quiz['total_marks']}"))

        start_button = QPushButton("Start Quiz")
        start_button.clicked.connect(lambda: self.start_quiz(quiz))
        self.question_layout.addWidget(start_button)

    # def start_quiz(self, quiz):
    #     """Start the quiz and load the questions."""
    #     self.load_questions(quiz['quiz_title'])
    #     self.time_left = int(quiz['total_time']) * 60
    #     self.timer = QTimer(self)
    #     self.timer.timeout.connect(self.update_timer)
    #     self.timer.start(1000)
    #     self.show_question()
    def start_quiz(self, quiz):
        """Start the quiz and load the questions."""
        self.load_questions(quiz['quiz_title'])
        total_minutes = float(quiz['total_time'])
        minutes = int(total_minutes)
        seconds = int((total_minutes - minutes) * 60)
        self.time_left = minutes * 60 + seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.show_question()

    def load_questions(self, quiz_title):
        """Load questions for the selected quiz."""
        try:
            with open('questions.json', 'r') as file:
                all_questions = json.load(file)
            self.questions = [q for q in all_questions if q['quiz_title'] == quiz_title]
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "questions.json not found.")
            sys.exit()

    def update_timer(self):
        """Update the timer every second."""
        if self.time_left > 0:
            self.time_left -= 1
            minutes, seconds = divmod(self.time_left, 60)
            self.timer_label.setText(f"Time Left: {minutes}:{seconds:02}")
        else:
            self.timer.stop()
            self.end_quiz()

    def show_question(self):
        """Display the current question."""
        self.clear_layout()
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            self.question_layout.addWidget(QLabel(f"Q{self.current_question_index + 1}: {question_data['question']}"))

            if question_data['question_type'] == "Multiple Correct Answer":
                self.show_multiple_correct_question(question_data)
            elif question_data['question_type'] == "True/False":
                self.show_true_false_question()
            else:
                self.show_text_input_question()

            self.add_navigation_buttons()
        else:
            self.end_quiz()

    def show_multiple_correct_question(self, question_data):
        """Show a multiple correct answer question."""
        self.checkboxes = []
        for option in question_data['answers']['options']:
            checkbox = QCheckBox(option)
            self.question_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

    def show_true_false_question(self):
        """Show a true/false question."""
        self.true_radio = QRadioButton("True")
        self.false_radio = QRadioButton("False")
        self.question_layout.addWidget(self.true_radio)
        self.question_layout.addWidget(self.false_radio)
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.true_radio)
        self.radio_group.addButton(self.false_radio)

    def show_text_input_question(self):
        """Show a text input question."""
        self.answer_field = QLineEdit()
        self.question_layout.addWidget(self.answer_field)

    def add_navigation_buttons(self):
        """Add navigation buttons."""
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.save_response_and_next)
        self.question_layout.addWidget(next_button)

        if self.current_question_index > 0:
            prev_button = QPushButton("Previous")
            prev_button.clicked.connect(self.go_to_previous_question)
            self.question_layout.addWidget(prev_button)

        end_button = QPushButton("End Quiz")
        end_button.clicked.connect(self.end_quiz)
        self.question_layout.addWidget(end_button)

    # def save_response_and_next(self):
    #     """Save the user's response and move to the next question."""
    #     self.save_user_response()
    #     self.current_question_index += 1
    #     self.show_question()
    def save_response_and_next(self):
        """Save the user's response and move to the next question."""
        self.save_user_response()

        # Check if the current question is the last one
        if self.current_question_index == len(self.questions) - 1:
            self.timer.stop()  # Stop the timer if it's the last question
            self.end_quiz()    # End the quiz immediately
        else:
            self.current_question_index += 1
            self.show_question()

    def go_to_previous_question(self):
        """Go to the previous question."""
        self.current_question_index -= 1
        self.show_question()

    def save_user_response(self):
        """Save the user's response for the current question."""
        question_data = self.questions[self.current_question_index]
        if question_data['question_type'] == "Multiple Correct Answer":
            selected = [i + 1 for i, checkbox in enumerate(self.checkboxes) if checkbox.isChecked()]
            self.user_responses[self.current_question_index] = selected
        elif question_data['question_type'] == "True/False":
            self.user_responses[self.current_question_index] = (
                "True" if self.true_radio.isChecked() else "False"
            )
        else:
            self.user_responses[self.current_question_index] = self.answer_field.text()

    def end_quiz(self):
        """End the quiz and show options for reviewing the quiz or closing."""
        self.clear_layout()

        # Store summary data when ending the quiz
        self.store_summary_data()

        # Add the Review button to review the quiz
        review_button = QPushButton("Review Quiz")
        review_button.clicked.connect(self.review_quiz)
        self.question_layout.addWidget(review_button)

        # Add the Close button to exit the quiz
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        self.question_layout.addWidget(close_button)

    def store_summary_data(self):
        """Store quiz summary data in summary.json."""
        summary_data = []  # Ensure the variable is defined here
        for i, question in enumerate(self.questions):
            user_answer = self.user_responses.get(i, "No answer")
            
            # Handle cases where answers might be a string or a dictionary
            answers = question.get('answers', {})
            if isinstance(answers, dict):  # If answers is a dictionary
                correct_answer = answers.get('correct_answers', "N/A")
                options = answers.get('options', [])
            else:  # If answers is a string
                correct_answer = answers
                options = []

            marks = question.get('marks', 0)
            
            summary_data.append({
                "question": question['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "marks": marks,
                "type": question.get('question_type', 'Unknown'),
                "options": options
            })

        # Log summary_data to debug
        print("Summary Data:", summary_data)

        try:
            with open("summary.json", "w") as file:
                json.dump(summary_data, file)
            print("Summary written to summary.json")  # Confirm writing
        except Exception as e:
            print(f"Error saving summary.json: {e}")
        
        summary_data.append({
                "Username":username,
                "quiz_title":title,
            })
        try:
            with open("total_summary.json", "a") as file:
                json.dump(summary_data, file, indent=7)
            print("Summary written to summary.json")  # Confirm writing
        except Exception as e:
            print(f"Error saving summary.json: {e}")
            

    def review_quiz(self):
        """Open the review window to display the summary."""
        self.review_quiz = QuizSummary()
        self.review_quiz.show()

    def clear_layout(self):
        """Clear all widgets from the question layout."""
        while self.question_layout.count():
            widget = self.question_layout.takeAt(0).widget()
            if widget:
                widget.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    username = "User"
    window = UserInterface(username)
    window.show()
    sys.exit(app.exec_())
