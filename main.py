from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QPushButton, QTextEdit, QVBoxLayout
)
from matcher import ResumeMatcherCore
import json
import psycopg2


class ResumeMatcherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.matcher = ResumeMatcherCore()
        self.results = []
        self.jd_path = None
        self.resume_folder = None
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

        self.btn_export = QPushButton("Export Results to PostgreSQL")
        self.btn_export.clicked.connect(self.export_to_postgres)
        self.layout.addWidget(self.btn_export)

        self.text_output = QTextEdit()
        self.layout.addWidget(self.text_output)

        self.setLayout(self.layout)

    def load_job_description(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Job Description", "", "Text Files (*.txt *.pdf *.docx)")
        if fname:
            self.jd_path = fname
            self.text_output.append(f"Loaded Job Description: {fname}")

    def load_resume_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Resume Folder")
        if folder:
            self.resume_folder = folder
            self.text_output.append(f"Loaded Resume Folder: {folder}")

    def run_matching(self):
        if not self.jd_path or not self.resume_folder:
            self.text_output.append("Please load both job description and resume folder first.")
            return

        self.text_output.append("Running matching, please wait...")
        self.results = self.matcher.run(self.jd_path, self.resume_folder)
        # print("HELLO",self.results)

        for res in self.results:
            file = res["filename"]
            data = res["score_data"]
            if "error" in data:
                output_text = f"[ERROR] {file} => {data['error']}"
                if "raw_response" in data:
                    output_text += f"\nRaw LLM Response:\n{data['raw_response']}"
                self.text_output.append(output_text)
            else:
                try:
                    pretty_json = json.dumps(data, indent=2)
                    output_text = f"{file} => Full Analysis:\n{pretty_json}"
                    self.text_output.append(output_text)
                except Exception as e:
                    output_text = f"{file} => Could not format output: {str(e)}"
                    self.text_output.append(output_text)

    def export_to_postgres(self):
        if not self.results:
            self.text_output.append("No results to export. Please run matching first.")
            return

        success = self.insert_into_postgres(self.results)

        if success:
            self.text_output.append("Successfully inserted results into PostgreSQL.")
        else:
            self.text_output.append("Failed to insert results into PostgreSQL.")

    def insert_into_postgres(self, results):
        db_config = {
            "dbname": "Resume_JD",
            "user": "postgres",
            "password": "admin",
            "host": "localhost",
            "port": 5433
        }

        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS resume_analysis (
                name TEXT,
                final_score FLOAT,
                technical_skills_score FLOAT,
                technical_skills TEXT,
                experience_score FLOAT,
                experience TEXT,
                education_score FLOAT,
                education TEXT,
                soft_skills_score FLOAT,
                soft_skills TEXT,
                certifications_score FLOAT,
                certifications TEXT,
                strengths TEXT,
                weaknesses TEXT,
                suggestions TEXT
            );
            """)

            for res in results:
                data = res.get("score_data", {})
                print(data)
                if "error" in data:
                    continue

                name = data.get("name", "")
                score = data.get("score", {})
                components = score.get("components", {})

                row = (
                    name,
                    score.get("value", 0.0),
                    components.get("technical_skills", {}).get("score", 0.0),
                    ", ".join(components.get("technical_skills", {}).get("matched", [])),
                    components.get("experience", {}).get("score", 0.0),
                    components.get("experience", {}).get("field", ""),
                    components.get("education", {}).get("score", 0.0),
                    components.get("education", {}).get("matched", ""),
                    components.get("soft_skills", {}).get("score", 0.0),
                    ", ".join(components.get("soft_skills", {}).get("matched", [])),
                    components.get("certifications", {}).get("score", 0.0),
                    ", ".join(components.get("certifications", {}).get("matched", [])),
                    ", ".join(data.get("analysis", {}).get("strengths", [])),
                    ", ".join(data.get("analysis", {}).get("weaknesses", [])),
                    ", ".join(data.get("analysis", {}).get("suggestions", [])),
                )

                cursor.execute("""
                    INSERT INTO resume_analysis (
                        name, final_score, technical_skills_score, technical_skills,
                        experience_score, experience, education_score, education,
                        soft_skills_score, soft_skills, certifications_score, certifications,
                        strengths, weaknesses, suggestions
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, row)

            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            print("DB Error:", e)
            return False


# Launch the GUI
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ResumeMatcherGUI()
    window.show()
    sys.exit(app.exec_())
