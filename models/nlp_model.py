import re
import spacy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

# ✅ Clean text
def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.lower().strip()

# ✅ Skill extraction
def extract_skills_from_text(text):
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'react', 'node', 'flask', 'django',
        'angular', 'vue', 'sql', 'mysql', 'mongodb', 'postgresql', 'git', 'github',
        'docker', 'kubernetes', 'api', 'rest', 'json', 'aws', 'azure', 'linux',
        'ml', 'machine learning', 'ai', 'nlp', 'data analysis', 'data science',
        'communication', 'problem solving', 'teamwork', 'debugging', 'testing'
    ]
    text_clean = clean_text(text)
    found = [skill for skill in common_skills if skill in text_clean]
    return sorted(list(set(found)))

# ✅ Hybrid Match Logic (ATS-Style)
def calculate_similarity(resume_text, job_text, resume_skills=None, job_skills=None):
    """
    Final ATS-accurate hybrid logic
    - 70% skill match ratio
    - 30% keyword/text similarity
    """
    # --- Clean Text ---
    resume_text = clean_text(resume_text)
    job_text = clean_text(job_text)

    # --- Skill-based Similarity ---
    resume_set = set([s.lower() for s in resume_skills])
    job_set = set([s.lower() for s in job_skills])
    matched = resume_set.intersection(job_set)

    skill_ratio = (len(matched) / len(job_set)) if job_set else 0
    skill_score = skill_ratio * 100

    # --- TF-IDF Text Similarity ---
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=3000)
        vectors = vectorizer.fit_transform([resume_text, job_text])
        text_score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100
    except:
        text_score = 0

    # --- Weighted Score ---
    if skill_ratio == 1.0:
        final_score = 100
    elif skill_ratio >= 0.8:
        final_score = 90 + (text_score * 0.05)
    elif skill_ratio >= 0.5:
        final_score = (0.7 * skill_score) + (0.3 * text_score)
    else:
        final_score = (0.5 * skill_score) + (0.5 * text_score)

    return round(final_score, 2)

# ✅ Recommendations
def generate_recommendations(extracted_skills, job_skills):
    missing = sorted(list(set(job_skills) - set(extracted_skills)))
    suggestions = []
    if missing:
        suggestions.append(f"Add or highlight: {', '.join(missing)}")
    return missing, suggestions
