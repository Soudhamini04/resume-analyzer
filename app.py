from flask import Flask, render_template, request, send_file
import PyPDF2
import docx
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

app = Flask(__name__)

# ---------------- ROLE SKILLS DATABASE ---------------- #
ROLE_SKILLS = {
    "Data Scientist": ["python", "machine learning", "deep learning", "pandas", "numpy", "tensorflow", "pytorch", "sql", "statistics"],
    "Web Developer": ["html", "css", "javascript", "react", "node", "flask", "django", "sql"],
    "AI Engineer": ["python", "deep learning", "nlp", "tensorflow", "pytorch", "machine learning"],
    "Software Engineer": ["java", "python", "c++", "data structures", "algorithms", "sql", "oop"],
    "Frontend Developer": ["html", "css", "javascript", "react", "angular", "vue", "bootstrap"],
    "Backend Developer": ["python", "java", "node", "django", "flask", "sql", "api", "microservices"],
    "DevOps Engineer": ["aws", "docker", "kubernetes", "jenkins", "ci/cd", "linux", "monitoring", "terraform"],
    "Mobile App Developer": ["android", "ios", "java", "kotlin", "swift", "flutter", "react native", "mobile ui"],
    "Cloud Engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd", "monitoring"],
    "Machine Learning Engineer": ["python", "machine learning", "tensorflow", "pytorch", "data preprocessing", "model deployment", "numpy", "pandas"]
}

IMPORTANT_SKILLS = ["python", "machine learning", "java", "aws", "docker"]

available_roles = list(ROLE_SKILLS.keys())

# ---------------- UTILITY FUNCTIONS ---------------- #
def extract_text(file):
    text = ""
    if file.filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text.strip() + " "
    elif file.filename.endswith('.docx'):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text.strip() + " "
    return text.lower()

def score_resume_for_role(resume_text, role):
    role_skills = [skill.lower() for skill in ROLE_SKILLS[role]]
    matched = []
    missing = []
    total_weight = 0
    obtained_weight = 0
    for skill in role_skills:
        weight = 2 if skill in IMPORTANT_SKILLS else 1
        total_weight += weight
        occurrences = resume_text.count(skill)
        if occurrences > 0:
            # Only append skill name, no count
            matched.append(skill)
            obtained_weight += weight
        else:
            missing.append(skill)
    score = int((obtained_weight / total_weight) * 100) if total_weight > 0 else 0
    return score, matched, missing

def analyze_top_roles(resume_text, top_n=3):
    role_scores = []
    for role in available_roles:
        score, matched, missing = score_resume_for_role(resume_text, role)
        role_scores.append({
            "role": role,
            "score": score,
            "matched": matched,
            "missing": missing
        })
    # Sort by score descending
    role_scores.sort(key=lambda x: x["score"], reverse=True)
    return role_scores[:top_n]

# ---------------- FLASK ROUTES ---------------- #
@app.route('/')
def home():
    return render_template("index.html", roles=available_roles)

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['resume']
    text = extract_text(file)
    top_roles = analyze_top_roles(text, top_n=3)
    return render_template("result.html", top_roles=top_roles)

@app.route('/download', methods=['POST'])
def download():
    import json
    top_roles_json = request.form['top_roles']
    top_roles = json.loads(top_roles_json)  # list of role dicts

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Resume Analysis Report", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    for role_info in top_roles:
        elements.append(Paragraph(f"Role: {role_info['role']}", styles['Heading2']))
        elements.append(Paragraph(f"ATS Score: {role_info['score']}%", styles['Normal']))
        if role_info['matched']:
            elements.append(Paragraph("Matched Skills:", styles['Heading3']))
            for skill in role_info['matched']:
                elements.append(Paragraph(f"- {skill}", styles['Normal']))
        if role_info['missing']:
            elements.append(Paragraph("Missing Skills:", styles['Heading3']))
            for skill in role_info['missing']:
                elements.append(Paragraph(f"- {skill}", styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="Resume_Report.pdf", mimetype='application/pdf')

# ---------------- RUN APP ---------------- #
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)