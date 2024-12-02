import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout,QScrollArea,
    QHBoxLayout, QMessageBox, QRadioButton, QButtonGroup, QCheckBox, QTextEdit
)
from PyQt5.QtCore import Qt

class AdminInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Management - Admin Interface")
        self.setGeometry(100, 100, 800, 600)
        self.dynamic_widgets = []  # To track dynamically created widgets
        self.init_ui()
        self.current_quiz_title = None
        self.questions_saved = False  # Track if any question was saved
        self.total_questions = 0
        self.total_marks = 0
        self.quiz_password = ""  # Password for the quiz

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Quiz Title
        self.title_label = QLabel("Quiz Title:")
        self.title_input = QLineEdit()

        # Quiz Password
        self.password_label = QLabel("Quiz Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password to access this quiz")

        # Total Time
        self.time_label = QLabel("Total Time (in minutes):")
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Enter total time for this quiz")

        # Question Type
        self.type_label = QLabel("Select Question Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Multiple Correct Answer", "True/False", "Short Answer", "Integer Type"])
        self.type_combo.currentTextChanged.connect(self.update_question_form)

        # Question Text
        self.question_label = QLabel("Enter Question:")
        self.question_input = QTextEdit()

        # Placeholder for dynamic question form
        self.dynamic_form = QVBoxLayout()

        # Total Marks
        self.marks_label = QLabel("Total Marks:")
        self.marks_input = QLineEdit()

        # Buttons
        self.save_button = QPushButton("Save Question")
        self.next_button = QPushButton("Remove Question")
        self.end_button = QPushButton("End Quiz Creation")

        # Add to layout
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.title_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.time_input)
        self.layout.addWidget(self.type_label)
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.question_input)
        self.layout.addLayout(self.dynamic_form)
        self.layout.addWidget(self.marks_label)
        self.layout.addWidget(self.marks_input)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.next_button)
        self.layout.addWidget(self.end_button)
        self.setLayout(self.layout)

        # Wrap main layout in a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create a widget to hold the main layout
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.layout)

        # Set the scrollable widget
        self.scroll_area.setWidget(self.scroll_widget)

        # Final layout for the main window
        self.final_layout = QVBoxLayout(self)
        self.final_layout.addWidget(self.scroll_area)
        self.setLayout(self.final_layout)

        # Connect buttons to actions
        self.save_button.clicked.connect(self.save_question)
        self.next_button.clicked.connect(self.clear_inputs)
        self.end_button.clicked.connect(self.end_quiz_creation)

        # Initialize question form
        self.update_question_form()

    def update_question_form(self):
        """Update the form based on the selected question type."""
        self.clear_dynamic_widgets()  # Clear previous dynamic widgets

        question_type = self.type_combo.currentText()

        if question_type == "Multiple Correct Answer":
            # Number of options
            MCQ.no(self)

        elif question_type == "True/False":
            T_F.fin(self)
        elif question_type in ["Short Answer", "Integer Type"]:
            Misc.fin(self)
    def save_question(self):
        """Save the current question to a JSON file."""
        title = self.title_input.text().strip()
        password = self.password_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Error", "Please enter a quiz title!")
            return

        if not password:
            QMessageBox.warning(self, "Error", "Please set a password for this quiz!")
            return

        self.current_quiz_title = title
        self.quiz_password = password
        question_type = self.type_combo.currentText()
        question = self.question_input.toPlainText().strip()
        marks = self.marks_input.text().strip()

        if not question :
            QMessageBox.warning(self, "Error", "Please fill in question")
            return
        if not marks :
            QMessageBox.warning(self, "Error", "Please fill in marks")
            return

        answers = None

        if question_type == "Multiple Correct Answer":
            answers = MCQ.check(self)
            if answers == None:
                return 
        elif question_type == "True/False":
            answers = T_F.cond(self)
            if answers == None:
                return  
        elif question_type in ["Short Answer", "Integer Type"]:
            answers= Misc.cond(self)
            if question_type == "Integer Type":
                try:
                    answers = int(answers) 
                except:
                    QMessageBox.warning(self, "Error", "Please fill in Integer answer")
                    return
            if answers == None:
                return


        try:
            # Save the question to questions.json
            question_details = {
                "quiz_title": title,
                "question_type": question_type,
                "question": question,
                "marks": int(marks),
                "answers": answers
            }

            # Load existing questions or create an empty list
            try:
                with open('questions.json', 'r') as file:
                    questions_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                questions_data = []

            questions_data.append(question_details)

            with open('questions.json', 'w') as file:
                json.dump(questions_data, file, indent=4)

            QMessageBox.information(self, "Success", "Question saved successfully!")
            self.questions_saved = True
            self.total_questions += 1
            self.total_marks += int(marks)
            self.clear_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save question: {str(e)}")

    def clear_dynamic_widgets(self, start_index=0):
        """Clear dynamic widgets starting from a specific index."""
        while len(self.dynamic_widgets) > start_index:
            widget = self.dynamic_widgets.pop()
            widget.deleteLater()

    def clear_inputs(self):
        """Clear input fields for the next question."""
        self.question_input.clear()
        self.marks_input.clear()
        self.update_question_form()

    def end_quiz_creation(self):
        """End quiz creation and save quiz details."""
        if not self.questions_saved:
            QMessageBox.warning(self, "Warning", "No questions were saved for this quiz!")
        else:
            total_time = self.time_input.text().strip()
            if not total_time:
                QMessageBox.warning(self, "Error", "Please specify the total time for the quiz!")
                return

            # Save quiz details to quizzes.json
            quiz_details = {
                "quiz_title": self.current_quiz_title,
                "quiz_password": self.quiz_password,
                "total_questions": self.total_questions,
                "total_marks": self.total_marks,
                "total_time": total_time
            }

            try:
                # Load existing quizzes or create an empty list
                try:
                    with open('quizzes.json', 'r') as file:
                        quizzes_data = json.load(file)
                except (FileNotFoundError, json.JSONDecodeError):
                    quizzes_data = []

                quizzes_data.append(quiz_details)

                with open('quizzes.json', 'w') as file:
                    json.dump(quizzes_data, file, indent=4)

                QMessageBox.information(
                    self,
                    "Quiz Summary",
                    f"Quiz Title: {self.current_quiz_title}\n"
                    f"Quiz Password: {self.quiz_password}\n"
                    f"Total Questions: {self.total_questions}\n"
                    f"Total Marks: {self.total_marks}\n"
                    f"Total Time: {total_time} minutes"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save quiz details: {str(e)}")
            
            self.close()

    def create_option_inputs(self):
        # Clear previous option inputs
        self.clear_dynamic_widgets(start_index=2)

        try:
            num_options = int(self.num_options_input.text())
            self.option_inputs = []
            self.correct_option_checkboxes = []

            for i in range(1, num_options + 1):
                option_layout = QHBoxLayout()
                option_label = QLabel(f"Option {i}:")
                option_input = QLineEdit()
                correct_checkbox = QCheckBox("Correct")

                option_layout.addWidget(option_label)
                option_layout.addWidget(option_input)
                option_layout.addWidget(correct_checkbox)

                self.dynamic_form.addLayout(option_layout)

                self.option_inputs.append(option_input)
                self.correct_option_checkboxes.append(correct_checkbox)
                self.dynamic_widgets.extend([option_label, option_input, correct_checkbox])
        except ValueError:
            pass  # Ignore non-integer input

class MCQ(AdminInterface):
    def __init__(self):
        super().__init__(self)
    
    def no(self):
        self.num_options_label = QLabel("Number of Options:")
        self.num_options_input = QLineEdit()
        self.num_options_input.setPlaceholderText("Enter number of options")
        self.num_options_input.textChanged.connect(self.create_option_inputs)

        self.dynamic_form.addWidget(self.num_options_label)
        self.dynamic_form.addWidget(self.num_options_input)

        self.dynamic_widgets.extend([self.num_options_label, self.num_options_input])

    def check(self):
        options = [option.text() for option in self.option_inputs if option.text().strip()]
        correct_answers = [i + 1 for i, checkbox in enumerate(self.correct_option_checkboxes) if checkbox.isChecked()]

        if not options or not correct_answers:
            QMessageBox.warning(self, "Error", "Please provide all options and select at least one correct answer!")
            return None

        return {"options": options, "correct_answers": correct_answers}

class T_F(AdminInterface):
    def __init__(self):
        super().__init__(self)
    
    def fin(self):
        # True/False radio buttons
        self.true_false_group = QButtonGroup(self)
        self.true_radio = QRadioButton("True")
        self.false_radio = QRadioButton("False")
        self.true_false_group.addButton(self.true_radio)
        self.true_false_group.addButton(self.false_radio)

        self.dynamic_form.addWidget(self.true_radio)
        self.dynamic_form.addWidget(self.false_radio)

        self.dynamic_widgets.extend([self.true_radio, self.false_radio])

    def cond(self):
        if self.true_radio.isChecked():
            return "True"
        elif self.false_radio.isChecked():
            return "False"
        else:
            QMessageBox.warning(self, "Error", "Please select True or False!")
            return None

class Misc(AdminInterface):
    def __init__(self):
        super().__init__(self)
    
    def fin(self):
        # Add input field for correct answer
        self.answer_label = QLabel("Enter Correct Answer:")
        self.answer_input = QLineEdit()
        self.dynamic_form.addWidget(self.answer_label)
        self.dynamic_form.addWidget(self.answer_input)

        self.dynamic_widgets.extend([self.answer_label, self.answer_input])

    def cond(self):
        answers = self.answer_input.text().strip()
        if not answers:
                QMessageBox.warning(self, "Error", "Please provide the correct answer!",QMessageBox.No )
                return None
        return answers

if __name__ == "__main__":
    app = QApplication(sys.argv)
    admin_window = AdminInterface()
    admin_window.show()
    sys.exit(app.exec_())