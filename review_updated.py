import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea


class QuizSummary(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz Summary")
        self.setGeometry(100, 100, 600, 800)

        layout = QVBoxLayout()

        # Load quiz summary from JSON file
        with open("summary.json", "r") as file:
            quiz_summary = json.load(file)

        # Initialize total marks variable
        total_marks = 0

        for idx, question in enumerate(quiz_summary):
            question_number = idx + 1
            question_type = question["type"]
            question_text = question["question"]
            user_answer = question["user_answer"]
            correct_answer = question["correct_answer"]
            marks = question["marks"]
            options = question["options"]

            # Calculate total marks
            if user_answer == correct_answer:
                total_marks += marks

            # Add labels for each field
            layout.addWidget(QLabel(f"{question_number}. Question Type: {question_type}"))
            layout.addWidget(QLabel(f"Question: {question_text}"))

            # Add options only if they exist
            if options:
                layout.addWidget(QLabel("Options:"))
                for i, option in enumerate(options):
                    layout.addWidget(QLabel(f"{i + 1}. {option}"))

            layout.addWidget(QLabel(f"Your Answer: {user_answer}"))
            layout.addWidget(QLabel(f"Correct Answer: {correct_answer}"))
            layout.addWidget(QLabel(f"Marks Obtained: {marks if user_answer == correct_answer else 0}"))
            layout.addWidget(QLabel("-" * 40))  # Separator between questions

        # Display total marks at the end
        layout.addWidget(QLabel(f"Total Marks: {total_marks}"))

        # Set up a scroll area in case of large summaries
        scroll_area = QScrollArea()
        container_widget = QWidget()
        container_widget.setLayout(layout)
        scroll_area.setWidget(container_widget)
        scroll_area.setWidgetResizable(True)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizSummary()
    window.show()
    sys.exit(app.exec_())
