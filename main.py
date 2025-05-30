#GUI

from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QPushButton, QTextEdit, QVBoxLayout
)
from matcher import ResumeMatcherCore
import json
import csv

class ResumeMatcherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.matcher = ResumeMatcherCore()
        self.results = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI Resume Matcher")
        self.layout = QVBoxLayout()

        self.btn_load_jd = QPushButton("Load Job Description")
        self.btn_load_jd.clicked.connect(self.load_job_description)
        self.layout.addWidget(self.btn_load_jd)

        self.btn_load_resumes = QPushButton("Load Resume Folder")
        self.btn_load_resumes.clicked.connect(self.load_resume_folder)
        self.layout.addWidget(self.btn_load_resumes)

        self.btn_run = QPushButton("Run Matching")
        self.btn_run.clicked.connect(self.run_matching)
        self.layout.addWidget(self.btn_run)

        self.btn_export = QPushButton("Export Results to CSV")
        self.btn_export.clicked.connect(self.export_to_csv)
        self.layout.addWidget(self.btn_export)

        self.text_output = QTextEdit()
        self.layout.addWidget(self.text_output)

        self.setLayout(self.layout)

        self.jd_path = None
        self.resume_folder = None

    def load_job_description(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Job Description", "", "Text Files (*.txt *.pdf *.docx)")
        if fname:
            self.jd_path = fname
            self.text_output.append(f"Loaded Job Description: {fname}")
            print(f"Loaded Job Description: {fname}")

    def load_resume_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Resume Folder")
        if folder:
            self.resume_folder = folder
            self.text_output.append(f"Loaded Resume Folder: {folder}")
            print(f"Loaded Resume Folder: {folder}")

    def run_matching(self):
        if not self.jd_path or not self.resume_folder:
            self.text_output.append("Please load both job description and resume folder first.")
            print("Please load both job description and resume folder first.")
            return

        self.text_output.append("Running matching, please wait...")
        print("Running matching, please wait...")
        self.results = self.matcher.run(self.jd_path, self.resume_folder)

        for res in self.results:
            file = res["filename"]
            data = res["score_data"]
            if "error" in data:
                output_text = f"[ERROR] {file} => {data['error']}"
                if "raw_response" in data:
                    output_text += f"\nRaw LLM Response:\n{data['raw_response']}"
                self.text_output.append(output_text)
                print(output_text)
            else:
                try:
                    pretty_json = json.dumps(data, indent=2)
                    output_text = f"{file} => Full Analysis:\n{pretty_json}"
                    self.text_output.append(output_text)
                    print(output_text)
                except Exception as e:
                    output_text = f"{file} => Could not format output: {str(e)}"
                    self.text_output.append(output_text)
                    print(output_text)

    def export_to_csv(self):
        if not self.results:
            self.text_output.append("No results to export. Please run matching first.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
        if not path:
            return

        headers = [
            "Filename", "Name", "Final Score", "Experience (Years)", "Experience Field",
            "Technical Skills", "Soft Skills", "Strengths", "Weaknesses", "Suggestions"
        ]

        try:
            with open(path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for res in self.results:
                    filename = res.get("filename", "")
                    data = res.get("score_data", {})

                    name = data.get("name", "")
                    score_value = data.get("score", {}).get("value", "")
                    experience = data.get("score", {}).get("components", {}).get("experience", {})
                    exp_years = experience.get("years", "")
                    exp_field = experience.get("field", "")

                    technical_skills = ", ".join(data.get("score", {}).get("components", {}).get("technical_skills", {}).get("matched", []))
                    soft_skills = ", ".join(data.get("score", {}).get("components", {}).get("soft_skills", {}).get("matched", []))

                    analysis = data.get("analysis", {})
                    strengths = ", ".join(analysis.get("strengths", []))
                    weaknesses = ", ".join(analysis.get("weaknesses", []))
                    suggestions = ", ".join(analysis.get("suggestions", []))

                    row = [
                        filename, name, score_value, exp_years, exp_field,
                        technical_skills, soft_skills, strengths, weaknesses, suggestions
                    ]
                    writer.writerow(row)

            self.text_output.append(f"Exported results to CSV at: {path}")
            print(f"Exported results to CSV at: {path}")

        except Exception as e:
            self.text_output.append(f"Error exporting to CSV: {e}")
            print(f"Error exporting to CSV: {e}")

# This part is essential for launching the GUI
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ResumeMatcherGUI()
    window.show()
    sys.exit(app.exec_())
