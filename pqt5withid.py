import sys
import os
import json
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QRadioButton, 
                             QButtonGroup, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class UserDataEntry(QWidget):
    def __init__(self):
        super().__init__()
        self.id_proof_path = ""
        self.data_file = "user_data.json"
        self.reports_dir = "user_reports"
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("User Data Entry")
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout()

        # Title
        title = QLabel("User Data Entry")
        title.setFont(QFont("Arial", 24))
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Name Entry
        self.name_entry = QLineEdit(self)
        self.name_entry.setPlaceholderText("Name")
        layout.addWidget(self.name_entry)

        # Age Entry
        self.age_entry = QLineEdit(self)
        self.age_entry.setPlaceholderText("Age")
        layout.addWidget(self.age_entry)

        # Gender Radio Buttons
        gender_label = QLabel("Gender:")
        layout.addWidget(gender_label)
        self.gender_group = QButtonGroup(self)
        self.male_radio = QRadioButton("Male")
        self.female_radio = QRadioButton("Female")
        self.gender_group.addButton(self.male_radio)
        self.gender_group.addButton(self.female_radio)
        layout.addWidget(self.male_radio)
        layout.addWidget(self.female_radio)

        # Qualification Entry
        self.qualification_entry = QLineEdit(self)
        self.qualification_entry.setPlaceholderText("Qualification")
        layout.addWidget(self.qualification_entry)

        # ID Proof Upload
        self.id_proof_button = QPushButton("Upload ID Proof (JPEG)")
        self.id_proof_button.clicked.connect(self.upload_id_proof)
        layout.addWidget(self.id_proof_button)
        self.id_proof_label = QLabel("No file selected")
        layout.addWidget(self.id_proof_label)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_data)
        layout.addWidget(self.submit_button)

        # View Reports Button
        self.view_reports_button = QPushButton("View Reports")
        self.view_reports_button.clicked.connect(self.view_reports)
        layout.addWidget(self.view_reports_button)

        self.setLayout(layout)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                self.data = json.load(file)
        else:
            self.data = []

        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def save_data(self):
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file, indent=2)

    def upload_id_proof(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select ID Proof", "", "JPEG files (*.jpg *.jpeg)")
        if file_path:
            self.id_proof_path = file_path
            file_name = os.path.basename(file_path)
            self.id_proof_label.setText(f"Selected: {file_name}")

    def submit_data(self):
        name = self.name_entry.text()
        age = self.age_entry.text()
        gender = "Male" if self.male_radio.isChecked() else "Female"
        qualification = self.qualification_entry.text()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not all([name, age, gender, qualification, self.id_proof_path]):
            QMessageBox.critical(self, "Error", "Please fill all fields and upload an ID proof.")
            return

        new_entry = {
            "name": name,
            "age": age,
            "gender": gender,
            "qualification": qualification,
            "timestamp": timestamp,
            "id_proof_path": self.id_proof_path
        }

        self.data.append(new_entry)
        self.save_data()
        pdf_path = self.generate_pdf_report(new_entry)

        QMessageBox.information(self, "Success", f"Data submitted successfully!\nPDF report generated: {pdf_path}")

        self.name_entry.clear()
        self.age_entry.clear()
        self.qualification_entry.clear()
        self.id_proof_label.setText("No file selected")
        self.id_proof_path = ""

    def generate_pdf_report(self, entry):
        pdf_filename = f"{entry['name']}_{entry['timestamp'].replace(':', '-')}.pdf"
        pdf_path = os.path.join(self.reports_dir, pdf_filename)

        # Register a Unicode font
        pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # Set font
        c.setFont("Arial", 12)

        # Title
        c.setFont("Arial", 16)
        c.drawString(50, height - 50, "User Report")
        c.setFont("Arial", 12)

        # User details
        c.drawString(50, height - 80, f"Name: {entry['name']}")
        c.drawString(50, height - 100, f"Age: {entry['age']}")
        c.drawString(50, height - 120, f"Gender: {entry['gender']}")
        c.drawString(50, height - 140, f"Qualification: {entry['qualification']}")
        c.drawString(50, height - 160, f"Timestamp: {entry['timestamp']}")

        # ID Proof image
        img = ImageReader(entry['id_proof_path'])
        img_width, img_height = img.getSize()
        aspect = img_height / float(img_width)
        display_width = 400
        display_height = display_width * aspect
        c.drawImage(img, 50, height - 160 - display_height, width=display_width, height=display_height)

        c.save()
        return pdf_path

    def view_reports(self):
        reports = [f for f in os.listdir(self.reports_dir) if f.endswith('.pdf')]
        if not reports:
            QMessageBox.information(self, "Info", "No reports available.")
            return

        if os.name == 'nt':  # For Windows
            os.startfile(self.reports_dir)
        elif os.name == 'posix':  # For macOS and Linux
            os.system(f"open {self.reports_dir}")
        else:
            QMessageBox.information(self, "Info", f"Please open this folder manually: {self.reports_dir}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UserDataEntry()
    window.show()
    sys.exit(app.exec_())
