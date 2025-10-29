import os
from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
from utils import extractors
from models.nlp_model import extract_skills_from_text, calculate_similarity, generate_recommendations
import spacy
import subprocess

# Ensure the spaCy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'.pdf', '.docx'}

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_text = request.form.get('job_text', '')
        job_skills_raw = request.form.get('job_skills', '')
        job_skills = [s.strip().lower() for s in job_skills_raw.split(',') if s.strip()]

        file = request.files.get('resume')
        if not file or file.filename == '':
            return render_template('index.html', error='Please upload a resume')

        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            return render_template('index.html', error='Unsupported file type')

        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        # --- Extract resume text ---
        resume_text = extractors.extract_text(path)

        # --- Extract skills from resume & JD ---
        resume_skills = extract_skills_from_text(resume_text)
        if not job_skills:
            job_skills = extract_skills_from_text(job_text)

        # --- Calculate accurate match ---
        similarity = calculate_similarity(resume_text, job_text, resume_skills, job_skills)

        # --- Generate Recommendations ---
        missing, suggestions = generate_recommendations(resume_skills, job_skills)

        result = {
            'similarity': similarity,
            'extracted_skills': resume_skills,
            'job_skills': job_skills,
            'missing_skills': missing,
            'suggestions': suggestions,
            'resume_filename': filename
        }

        return render_template('result.html', result=result)

    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
