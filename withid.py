import customtkinter as ctk
from tkinter import messagebox, filedialog
import datetime
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UserDataEntry:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("User Data Entry")
        self.root.geometry("400x650")
        self.id_proof_path = ""
        self.data_file = "user_data.json"
        self.reports_dir = "user_reports"
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        title = ctk.CTkLabel(main_frame, text="User Data Entry", font=("Roboto", 24))
        title.pack(pady=10)

        self.name_entry = ctk.CTkEntry(main_frame, placeholder_text="Name")
        self.name_entry.pack(pady=10, padx=20, fill="x")

        self.age_entry = ctk.CTkEntry(main_frame, placeholder_text="Age")
        self.age_entry.pack(pady=10, padx=20, fill="x")

        self.gender_var = ctk.StringVar(value="Male")
        gender_frame = ctk.CTkFrame(main_frame)
        gender_frame.pack(pady=10, padx=20, fill="x")
        gender_label = ctk.CTkLabel(gender_frame, text="Gender:")
        gender_label.pack(side="left", padx=(0, 10))
        male_radio = ctk.CTkRadioButton(gender_frame, text="Male", variable=self.gender_var, value="Male")
        male_radio.pack(side="left", padx=(0, 10))
        female_radio = ctk.CTkRadioButton(gender_frame, text="Female", variable=self.gender_var, value="Female")
        female_radio.pack(side="left")

        self.qualification_entry = ctk.CTkEntry(main_frame, placeholder_text="Qualification")
        self.qualification_entry.pack(pady=10, padx=20, fill="x")

        id_proof_frame = ctk.CTkFrame(main_frame)
        id_proof_frame.pack(pady=10, padx=20, fill="x")
        id_proof_label = ctk.CTkLabel(id_proof_frame, text="ID Proof (JPEG):")
        id_proof_label.pack(side="left", padx=(0, 10))
        self.id_proof_button = ctk.CTkButton(id_proof_frame, text="Upload", command=self.upload_id_proof)
        self.id_proof_button.pack(side="left")
        self.id_proof_name_label = ctk.CTkLabel(main_frame, text="No file selected")
        self.id_proof_name_label.pack(pady=(0, 10))

        submit_button = ctk.CTkButton(main_frame, text="Submit", command=self.submit_data)
        submit_button.pack(pady=10, padx=20, fill="x")

        view_reports_button = ctk.CTkButton(main_frame, text="View Reports", command=self.view_reports)
        view_reports_button.pack(pady=10, padx=20, fill="x")

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
        file_path = filedialog.askopenfilename(filetypes=[("JPEG files", "*.jpg *.jpeg")])
        if file_path:
            self.id_proof_path = file_path
            file_name = os.path.basename(file_path)
            self.id_proof_name_label.configure(text=f"Selected: {file_name}")

    def submit_data(self):
        name = self.name_entry.get()
        age = self.age_entry.get()
        gender = self.gender_var.get()
        qualification = self.qualification_entry.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not all([name, age, gender, qualification, self.id_proof_path]):
            messagebox.showerror("Error", "Please fill all fields and upload an ID proof.")
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

        messagebox.showinfo("Success", f"Data submitted successfully!\nPDF report generated: {pdf_path}")

        self.name_entry.delete(0, ctk.END)
        self.age_entry.delete(0, ctk.END)
        self.qualification_entry.delete(0, ctk.END)
        self.id_proof_path = ""
        self.id_proof_name_label.configure(text="No file selected")

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
        if not self.data:
            messagebox.showinfo("Info", "No reports available.")
            return

        reports = [f for f in os.listdir(self.reports_dir) if f.endswith('.pdf')]
        if not reports:
            messagebox.showinfo("Info", "No reports available.")
            return

        # Open the reports directory
        if os.name == 'nt':  # For Windows
            os.startfile(self.reports_dir)
        elif os.name == 'posix':  # For macOS and Linux
            subprocess.call(('open', self.reports_dir))
        else:
            messagebox.showinfo("Info", f"Please open this folder manually: {self.reports_dir}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = UserDataEntry()
    app.run()